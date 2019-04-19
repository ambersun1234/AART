# jersyTracking.py
defaultModelFolder = "/home/louisme/library/openpose/models/"
darknetCfg = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/yolov3.cfg"
darnetWeights = "/home/louisme/library/yolov3/AART_project/yolov3_weights/yolov3_20000.weights"
darknetData = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/obj.data"


# darknet.py
darknetDir = "/home/louisme/library/darknet/"

# obj.data
arr = dict.fromkeys(["trainLocation", "testLocation", "namesLocation", "backupLocation"], None)
objdataLocation = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/obj.data"
arr["trainLocation"] = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/train.txt"
arr["validLocation"] = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/test.txt"
arr["namesLocation"] = "/home/louisme/library/yolov3/AART_project/yolov3TrainingSrc/obj.names"
arr["backupLocation"] = "/home/louisme/library/yolov3/AART_project/yolov3_weights/yolov3_20000.weights"

# read-only area
if __name__ == "__main__":
    lines = []
    try:
        with open(objdataLocation, "r") as fp:
            lines = fp.readlines()
            fp.close()
    except IOError:
        print(objdataLocation + " not found")

    with open(objdataLocation, "w") as f:
        count = 1
        for element in lines:
            if count == 1:
                f.write(element)
                count += 1
            else:
                f.write(element.split('=')[0] + '=' + str(arr[element.split('=')[0] + "Location"]) + '\n')
        f.close()
