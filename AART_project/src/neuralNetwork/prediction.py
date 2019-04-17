import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import tensorflow as tf
import sys
import os
import cv2
from sklearn import metrics

from src.darknet import *

try:
    sys.path.append('/usr/local/python')
    from openpose import pyopenpose as openpose
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` '
          'in CMake and have this Python script in the right folder?')
    raise e


class runNeuralNetwork:
    def __init__(self):
        params = dict()
        params["model_folder"] = "/home/louisme/library/openpose/models"
        opWrapper = openpose.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
        datum = openpose.Datum()
        self.opWrapper = opWrapper
        self.datum = datum
        self.net = load_net(b"/home/louisme/library/darknet/jerseyNumber/cfg/yolov3.cfg",
                           b"/home/louisme/library/darknet/jerseyNumber/cfg/weights/yolov3_20000.weights",
                           0)
        self.meta = load_meta(b"/home/louisme/library/darknet/jerseyNumber/cfg/obj.data")
        self.keypointHistory = dict()
        self.shootingCount = 1
        self.layupCount = 1
        self.dribbleCount = 1
        self.saveVideo = dict()

        with tf.Graph().as_default():
            graph0 = tf.GraphDef()
            pb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frozen_har.pb')
            with open(pb_path, mode='rb') as f:
                graph0.ParseFromString(f.read())
                tf.import_graph_def(graph0, name='')
            sess = tf.Session()
            init = tf.global_variables_initializer()
            sess.run(init)
            input = sess.graph.get_tensor_by_name('input:0')
            y = sess.graph.get_tensor_by_name('y_:0')
            self.sessLSTM = sess
            self.inputLSTM = input
            self.y_LSTM = y

    def trackNum(self, specific, specific_num, frame):
        result = detect(self.net, self.meta, frame)
        self.datum.cvInputData = frame
        self.opWrapper.emplaceAndPop([self.datum])
        keypoints = self.datum.poseKeypoints
        self.outputFrame = self.datum.cvOutputData
        retFrame = dict()
        retLSTM = dict()
        numberTmp = []
        if specific == 1:
            for key in specific_num:
                numberTmp.append(specific_num[key])

        for i in result:
            # Judge whether the person is who we want
            if specific == 1:
                if i[0].decode() not in numberTmp:
                    continue
            num = i[0].decode()
            personNum = 'person{}'.format(num)

            x, y, w, h = i[2][0], i[2][1], i[2][2], i[2][3]
            xmin, ymin, xmax, ymax = self.convertBack(float(x), float(y), float(w), float(h))
            for j in range(len(keypoints)):
                if keypoints[j][1][2] != 0 and x - 50 <= keypoints[j][1][0] <= x + 50 and ymin - 50 <= keypoints[j][1][1] <= ymin + 50:
                    normalizedPoint, poseture = self.normalize(keypoints[j])
                    retFrame[str(num)] = poseture
                    # Save the keypoints to the txt for LSTM detect
                    if personNum not in self.keypointHistory:
                        self.keypointHistory[personNum] = [[]]
                        self.saveVideo[personNum] = [frame]
                        for pointNum in range(len(normalizedPoint)):
                            if 8 >= pointNum >= 1 or 11 >= pointNum >= 10 or 14 >= pointNum >= 13:
                                self.keypointHistory[personNum][0].append(normalizedPoint[pointNum][0])
                                self.keypointHistory[personNum][0].append(normalizedPoint[pointNum][1])
                    else:
                        lines = len(self.keypointHistory[personNum])
                        if lines < 61:
                            self.keypointHistory[personNum].append([])
                            self.saveVideo[personNum].append(frame)
                            for pointNum in range(len(normalizedPoint)):
                                if 8 >= pointNum >= 1 or 11 >= pointNum >= 10 or 14 >= pointNum >= 13:
                                    self.keypointHistory[personNum][lines].append(normalizedPoint[pointNum][0])
                                    self.keypointHistory[personNum][lines].append(normalizedPoint[pointNum][1])
                        else:
                            lstmPrediction = self.recognizeLSTM(self.keypointHistory[personNum])
                            if lstmPrediction != 'none':
                                retLSTM[num] = lstmPrediction
                                self.keypointHistory.pop(personNum, None)
                                self.writeVideo(personNum, lstmPrediction)
                                self.saveVideo[personNum].clear()
                                continue
                            tmp = self.keypointHistory[personNum][1:]
                            lines = 60
                            self.keypointHistory[personNum] = tmp
                            self.keypointHistory[personNum].append([])
                            del self.saveVideo[personNum][0]
                            self.saveVideo[personNum].append(frame)
                            for pointNum in range(len(normalizedPoint)):
                                if 8 >= pointNum >= 1 or 11 >= pointNum >= 10 or 14 >= pointNum >= 13:
                                    self.keypointHistory[personNum][lines].append(normalizedPoint[pointNum][0])
                                    self.keypointHistory[personNum][lines].append(normalizedPoint[pointNum][1])
        return retFrame, retLSTM

    # Calculate the yolov3 return value to rectangle of the number
    def convertBack(self, x, y, w, h):
        xmin = int(round(x - (w / 2)))
        xmax = int(round(x + (w / 2)))
        ymin = int(round(y - (h / 2)))
        ymax = int(round(y + (h / 2)))
        return xmin, ymin, xmax, ymax

    def normalize(self, keypoints):
        outputWidth = 150
        outputHeight = 600
        height, width, channel = self.outputFrame.shape
        maxX = 0
        minX = width
        maxY = 0
        minY = height
        ret = np.zeros((25, 2))

        count = 0
        for points in keypoints:
            x = math.floor(points[0])
            y = math.floor(points[1])
            confidence = points[2]

            maxX = x if x > maxX and confidence != 0 else maxX
            minX = x if x < minX and confidence != 0 else minX
            maxY = y if y > maxY and confidence != 0 else maxY
            minY = y if y < minY and confidence != 0 else minY

            if confidence == 0:
                ret[count][0] = -1
                ret[count][1] = -1
            else:
                ret[count][0] = int(x)
                ret[count][1] = int(y)

            count += 1

        minY = minY - 5 if minY - 5 > 0 else 0
        maxY = maxY + 5 if maxY + 5 < height else height - 1
        minX = minX - 5 if minX - 5 > 0 else 0
        maxX = maxX + 5 if maxX + 5 < width else width - 1

        frame = self.outputFrame[minY:maxY, minX:maxX].copy()
        ret = ret.astype(int)
        extractHeight = maxY - minY
        extractWidth = maxX - minX
        # print(extractWidth, ' ', extractHeight)
        for i in range(25):
            if ret[i][0] != -1 and ret[i][1] != -1:
                # convert to relative coordinate ( origin photo
                ret[i][0] = int(ret[i][0] - minX)
                ret[i][1] = int(ret[i][1] - minY)
                # resize coordinate to normalize image
                ret[i][0] = int(round(ret[i][0] * (outputWidth / extractWidth)))
                ret[i][1] = int(round(ret[i][1] * (outputHeight / extractHeight)))

                ret[i][0] = ret[i][0] if ret[i][0] < outputWidth else outputWidth - 1
                ret[i][1] = ret[i][1] if ret[i][1] < outputHeight else outputHeight - 1

        return ret, frame

    def recognizeLSTM(self, list):
        columns = ['neck_x', 'neck_y',
                   'shoulderR_x', 'shoulderR_y',
                   'elbowR_x', 'elbowR_y',
                   'handR_x', 'handR_y',
                   'shoulderL_x', 'shoulderL_y',
                   'elbowL_x', 'elbowL_y',
                   'handL_x', 'handL_y',
                   'ass_x', 'ass_y',
                   'kneeR_x', 'kneeR_y',
                   'feetR_x', 'feetR_y',
                   'kneeL_x', 'kneeL_y',
                   'feetL_x', 'feetL_y']
        df = DataFrame(data=list, columns=columns)

        time_steps = 60
        # 50 data for one input
        n_features = 24
        segments = []
        for i in range(0, len(df) - time_steps):
            neck_x = df['neck_x'].values[i: i + time_steps]
            neck_y = df['neck_y'].values[i: i + time_steps]
            shoulderr_x = df['shoulderR_x'].values[i: i + time_steps]
            shoulderr_y = df['shoulderR_y'].values[i: i + time_steps]
            elbowr_x = df['elbowR_x'].values[i: i + time_steps]
            elbowr_y = df['elbowR_y'].values[i: i + time_steps]
            handr_x = df['handR_x'].values[i: i + time_steps]
            handr_y = df['handR_y'].values[i: i + time_steps]
            shoulderl_x = df['shoulderL_x'].values[i: i + time_steps]
            shoulderl_y = df['shoulderL_y'].values[i: i + time_steps]
            elbowl_x = df['elbowL_x'].values[i: i + time_steps]
            elbowl_y = df['elbowL_y'].values[i: i + time_steps]
            handl_x = df['handL_x'].values[i: i + time_steps]
            handl_y = df['handL_y'].values[i: i + time_steps]
            ass_x = df['ass_x'].values[i: i + time_steps]
            ass_y = df['ass_y'].values[i: i + time_steps]
            kneer_x = df['kneeR_x'].values[i: i + time_steps]
            kneer_y = df['kneeR_y'].values[i: i + time_steps]
            feetr_x = df['feetR_x'].values[i: i + time_steps]
            feetr_y = df['feetR_y'].values[i: i + time_steps]
            kneel_x = df['kneeL_x'].values[i: i + time_steps]
            kneel_y = df['kneeL_y'].values[i: i + time_steps]
            feetl_x = df['feetL_x'].values[i: i + time_steps]
            feetl_y = df['feetL_y'].values[i: i + time_steps]

            segments.append([neck_x, neck_y, shoulderr_x, shoulderr_y, elbowr_x, elbowr_y,
                             handr_x, handr_y, shoulderl_x, shoulderl_y, elbowl_x, elbowl_y, handl_x, handl_y,
                             ass_x, ass_y, kneer_x, kneer_y, feetr_x, feetr_y,
                             kneel_x, kneel_y, feetl_x, feetl_y])

        reshaped_segments = np.asarray(segments, dtype=np.float32).reshape(-1, time_steps, n_features)
        prediction = self.sessLSTM.run(self.y_LSTM, feed_dict={self.inputLSTM: reshaped_segments})
        prediction = prediction[0]
        if prediction[0] >= prediction[1] and prediction[0] >= prediction[2] and prediction[0] > 0.7:
            prediction = 'dribbling'
        elif prediction[1] >= prediction[0] and prediction[1] >= prediction[2] and prediction[1] > 0.7:
            prediction = 'layup'
        elif prediction[2] >= prediction[0] and prediction[2] >= prediction[1] and prediction[2] > 0.7:
            prediction = 'shooting'
        else:
            prediction = 'none'

        return prediction

    def writeVideo(self, personNum, activity):
        pathSave = os.path.dirname(os.path.abspath(__file__))
        pathSave = os.path.dirname(pathSave)
        pathSave = os.path.dirname(pathSave)
        count = 0
        if activity == 'dribbling':
            count = self.dribbleCount
            self.dribbleCount += 1
        elif activity == 'layup':
            count = self.layupCount
            self.layupCount += 1
        else:
            count = self.shootingCount
            self.shootingCount += 1
        pathSave = os.path.join(pathSave, 'video_save', '{}{}-{}.mp4'.format(activity, str(count), personNum))
        height, width, channel = self.saveVideo[personNum][0].shape
        size = (width, height)
        videoWriter = cv2.VideoWriter(pathSave, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, size)
        for frame in self.saveVideo[personNum]:
            videoWriter.write(frame)
        videoWriter.release()
