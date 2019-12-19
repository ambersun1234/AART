import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import tensorflow as tf
import sys
import os
import cv2
import math

from darknet import *
from config.yoloConfig import *

try:
    sys.path.append('/usr/local/python')
    from openpose import pyopenpose as openpose
except ImportError as e:
    print('Error: OpenPose library could not be found. '
          'Did you enable `BUILD_PYTHON` '
          'in CMake and have this Python script in the right folder?')
    raise e


class runNeuralNetwork:
    def __init__(self):
        params = dict()
        params["model_folder"] = defaultModelFolder
        opWrapper = openpose.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
        datum = openpose.Datum()
        self.opWrapper = opWrapper
        self.datum = datum
        self.net = load_net(
            darknetCfg.encode('utf-8'),
            darnetWeights.encode('utf-8'),
            0
        )
        self.meta = load_meta(darknetData.encode('utf-8'))
        self.keypointHistory = dict()
        self.shootingCount = 1
        self.dribbleCount = 1
        self.saveVideo = dict()
        self.frameCount = 0
        self.shootPerson = None
        self.shootRate = dict()

        # input temp, modify by panels
        self._idict = None
        # input track dict, e.g. {"person": "11"}
        self._iimg = None
        # input image: origin showed image
        self._imode = None
        # input mode: 0 or 1 indicate whether there is tracker

        # output temp, retrieve by panels
        self._odict = None
        self._oimg = None

        with tf.Graph().as_default():
            graph0 = tf.GraphDef()
            pb_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                'frozen_har.pb'
            )
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
        self.frameCount += 1
        result = detect(self.net, self.meta, frame)
        self.datum.cvInputData = frame
        keypoints = self.datum.poseKeypoints
        self.opWrapper.emplaceAndPop([self.datum])
        try:
            lala = len(keypoints)
        except BaseException as e:
            return

        self.outputFrame = self.datum.cvOutputData
        retFrame = dict()
        retLSTM = dict()
        numberTmp = []
        if specific == 1:
            for key in specific_num:
                numberTmp.append(specific_num[key])

        handBallDist = []
        ballX, ballY, ballW, ballH = 0, 0, 0, 0
        ballXMin, ballYMin, ballXMax, ballYMax = 0, 0, 0, 0
        hoopX, hoopY, hoopW, hoopH = 0, 0, 0, 0
        hoopXMin, hoopYMin, hoopXMax, hoopYMax = 0, 0, 0, 0
        for row in result:
            if row[0].decode() == 'ball':
                ballX, ballY, ballW, ballH = row[2][0], row[2][1], row[2][2], row[2][3]
                ballXMin, ballYMin, ballXMax, ballYMax = self.convertBack(
                    float(ballX),
                    float(ballY),
                    float(ballW),
                    float(ballH)
                )
            elif row[0].decode() == 'hoop':
                hoopX, hoopY, hoopW, hoopH = row[2][0], row[2][1], row[2][2], row[2][3]
                hoopXMin, hoopYMin, hoopXMax, hoopYMax = self.convertBack(
                    float(hoopX),
                    float(hoopY),
                    float(hoopW),
                    float(hoopH)
                )


        for j in range(len(keypoints)):
            if keypoints[j][4][2] != 0 or keypoints[j][7][2] != 0:
                handBallDist.append(
                    [self.handBallDistCul(ballX, ballY, keypoints[j]), j]
                )
        handBallDist.sort()

        # shootPerson = [A, B]
        # A為投籃的球員號碼
        # B為抓到投籃時的frame為多少
        # shootRate[C] = [D, E]
        # C為球員號碼
        # D為投球數量
        # E為進球數量
        if self.shootPerson is not None and\
            self.shootPerson[1] - self.frameCount < 30:
            overlap = self.overlap(ballXMin, ballYMin, ballXMax, ballYMax,
                         hoopXMin, hoopYMin, hoopXMax, hoopYMax)
            if overlap > 0.7:
                if self.shootRate.get(self.shootPerson[0], None) != None:
                    tmp = self.shootRate[self.shootPerson[0]]
                    self.shootRate[self.shootPerson[0]] = [tmp[0]+1, tmp[1]+1]
                else:
                    self.shootRate[self.shootPerson[0]] = [1, 1]
        elif self.shootPerson is not None and\
            self.shootPerson[1] - self.frameCount >= 30:
            if self.shootRate.get(self.shootPerson[0], None) != None:
                tmp = self.shootRate[self.shootPerson[0]]
                self.shootRate[self.shootPerson[0]] = [tmp[0]+1, tmp[1]]
            else:
                self.shootRate[self.shootPerson[0]] = [1, 0]
                self.shootPerson = None


        for i in result:
            # Judge whether the person is who we want
            if specific == 1:
                if i[0].decode() not in numberTmp or\
                    not i[0].decode().isdigit():
                    continue
            elif not i[0].decode().isdigit():
                continue

            num = i[0].decode()

            x, y, w, h = i[2][0], i[2][1], i[2][2], i[2][3]
            xmin, ymin, xmax, ymax = self.convertBack(
                float(x),
                float(y),
                float(w),
                float(h)
            )
            if num == '4':
                color = self.testColor(frame[ymin:ymax, xmin:xmax].copy())
                if color == 'Y':
                    num = '444'
                else:
                    num = '433'
                personNum = 'person{}{}'.format(num, color)
            else:
                personNum = 'person{}'.format(num)

            for j in range(len(keypoints)):
                if keypoints[j][1][2] != 0 and \
                        x - 50 <= keypoints[j][1][0] <= x + 50 \
                        and y - 50 <= keypoints[j][1][1] <= y + 50:
                    normalizedPoint, poseture = self.normalize(keypoints[j])
                    retFrame[str(num)] = poseture

                if keypoints[j][1][2] != 0 and \
                        x - 50 <= keypoints[j][1][0] <= x + 50 \
                        and y - 50 <= keypoints[j][1][1] <= y + 50\
                        and j == handBallDist[0][1]\
                        and handBallDist[0][0] < 100:
                    # Save the keypoints to the list for LSTM detect
                    if personNum not in self.keypointHistory:
                        lines = 0
                        self.keypointHistory[personNum] = [[]]
                        self.saveVideo[personNum] = [frame]
                    else:
                        lines = len(self.keypointHistory[personNum])
                        self.keypointHistory[personNum].append([])
                        self.saveVideo[personNum].append(frame)

                    for pointNum in range(len(normalizedPoint)):
                        # 擷取所需骨架
                        if 8 >= pointNum >= 1 or \
                                11 >= pointNum >= 10 or \
                                14 >= pointNum >= 13:
                            self.keypointHistory[personNum][lines].append(
                                normalizedPoint[pointNum][0]
                            )
                            self.keypointHistory[personNum][lines].append(
                                normalizedPoint[pointNum][1]
                            )
                    lstmPrediction = self.recognizeLSTM(
                        self.keypointHistory[personNum]
                    )
                    # print(lstmPrediction)
                    if lstmPrediction != 'none':
                        if lstmPrediction == 'shooting':
                            self.shootPerson = [num, self.frameCount]
                        retLSTM[num] = lstmPrediction
                        self.keypointHistory.pop(personNum, None)
                        self.writeVideo(personNum, lstmPrediction)
                        self.saveVideo[personNum].clear()
        self._odict = retLSTM
        self._oimg = retFrame  # h=204, w=164

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

        # minY = minY - 5 if minY - 5 > 0 else 0
        # maxY = maxY + 5 if maxY + 5 < height else height - 1
        # minX = minX - 5 if minX - 5 > 0 else 0
        # maxX = maxX + 5 if maxX + 5 < width else width - 1

        # Make output specific person picture beautiful
        # frameOutMinY = minY
        # frameOutMaxY = maxY
        # if keypoints[1][2] != 0 and keypoints[8][2] != 0:
        #     minYTmp = int(
        #         keypoints[1][1] - (keypoints[8][1] - keypoints[1][1])
        #     )
        #     maxYTmp = int(
        #         keypoints[8][1] + (keypoints[8][1] - keypoints[1][1])
        #     )
        #     maxYTmp *= 5
        #     frameOutMinY = minYTmp if minYTmp > 0 else 0
        #     frameOutMaxY = maxYTmp if maxYTmp < height else height - 1
        outH = 204
        outW = 164
        plusH = math.floor((outH - (maxY - minY)) / 2)
        plusW = math.floor((outW - (maxX - minX)) / 2)
        minY = minY - plusH if minY - plusH > 0 else 0
        maxY = maxY + plusH if maxY + plusH < height else height - 1
        minX = minX - plusW if minX - plusW > 0 else 0
        maxX = maxX + plusW if maxX + plusW < width else width - 1

        # print(frameOutMaxY - frameOutMinY)
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
                ret[i][0] = int(
                    round(
                        ret[i][0] * (outputWidth / extractWidth)
                    )
                )
                ret[i][1] = int(
                    round(
                        ret[i][1] * (outputHeight / extractHeight)
                    )
                )

                ret[i][0] = ret[i][0] \
                    if ret[i][0] < outputWidth \
                    else outputWidth - 1
                ret[i][1] = ret[i][1] \
                    if ret[i][1] < outputHeight \
                    else outputHeight - 1

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

        time_steps = 10
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

            segments.append(
                [
                    neck_x, neck_y, shoulderr_x, shoulderr_y,
                    elbowr_x, elbowr_y, handr_x, handr_y,
                    shoulderl_x, shoulderl_y, elbowl_x, elbowl_y,
                    handl_x, handl_y, ass_x, ass_y,
                    kneer_x, kneer_y, feetr_x, feetr_y,
                    kneel_x, kneel_y, feetl_x, feetl_y
                ]
            )

        reshaped_segments = np.asarray(
            segments,
            dtype=np.float32
        ).reshape(-1, time_steps, n_features)
        prediction = self.sessLSTM.run(
            self.y_LSTM,
            feed_dict={
                self.inputLSTM: reshaped_segments
            }
        )
        if len(prediction) > 0:
            prediction = prediction[0]
            if prediction[0] >= prediction[1] and \
                    prediction[0] > 0.7:
                prediction = 'dribbling'
            elif prediction[1] >= prediction[0] and \
                    prediction[1] > 0.7:
                prediction = 'shooting'
            else:
                prediction = 'none'
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
        else:
            count = self.shootingCount
            self.shootingCount += 1
        pathSave = os.path.join(
            pathSave,
            'video_save',
            '{}{}-{}.mp4'.format(
                activity,
                str(count),
                personNum
            )
        )
        height, width, channel = self.saveVideo[personNum][0].shape
        size = (width, height)
        videoWriter = cv2.VideoWriter(
            pathSave,
            cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
            30,
            size
        )
        for frame in self.saveVideo[personNum]:

            videoWriter.write(frame)
        videoWriter.release()

    def handBallDistCul(self, x, y, keypoint):
        ret = 1000000
        if keypoint[4][2] != 0:
            rightDist = math.sqrt(pow(x - keypoint[4][0], 2) + pow(y - keypoint[4][1], 2))
        else:
            rightDist = -1
        if keypoint[7][2] != 0:
            leftDist = math.sqrt(pow(x - keypoint[7][0], 2) + pow(y - keypoint[7][1], 2))
        else:
            leftDist = -1

        if rightDist != -1 and rightDist < ret:
            ret = rightDist
        if leftDist != -1 and leftDist < ret:
            ret = leftDist
        return ret

    def overlap(self, leftTopX1, leftTopY1, rightBottomX1, rightBottomY1,
                      leftTopX2, leftTopY2, rightBottomX2, rightBottomY2):
        x0 = max(leftTopX1, leftTopX2)
        x1 = min(rightBottomX1, rightBottomX2)
        y0 = max(leftTopY1, leftTopY2)
        y1 = min(rightBottomY1, rightBottomY2)
        if x0 >= x1 or y0 >= y1:
            return 0.0
        areaInt = (x1 - x0) * (y1 - y0)
        return areaInt / ((rightBottomX1-leftTopX1)*(rightBottomY1-leftTopY1) +\
                            (rightBottomX2-leftTopX2)*(rightBottomY2-leftTopY2) - areaInt)

    def testColor(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_blue=np.array([78,43,46])
        upper_blue=np.array([110,255,255])
        lower_yellow = np.array([10, 50, 50])
        upper_yellow = np.array([30, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_count = 0
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        yellow_count = 0
        h, w = mask_blue.shape
        # cv2.imshow('test', mask_blue)
        for i in range(h):
            x = mask_blue[i, int(w/2)]
            if x == 255:
                blue_count += 1
            x= mask_yellow[i, int(w/2)]
            if x == 255:
                yellow_count += 1
        if blue_count > yellow_count:
            return 'B'
        else:
            return 'Y'
