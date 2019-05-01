import sys
import time
import cv2

try:
    sys.path.append('/usr/local/python')
    from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` '
          'in CMake and have this Python script in the right folder?')
    raise e

# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "/home/louisme/library/openpose/models"


if __name__ == '__main__' :
    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    cap = cv2.VideoCapture('/home/louisme/PycharmProjects/takePicture/video.mp4')
    while True:
        start = time.time()
        ret, imageToProcess = cap.read()
        if not ret:
            break
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])

        # Display Image
        end = time.time()
        # print("Body keypoints: \n" + str(datum.poseKeypoints))
        output = datum.cvOutputData
        cv2.putText(output, str(1/(end-start)), (20,20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("frame", output)
        q = cv2.waitKey(1)
        if q == ord('q'):
            break