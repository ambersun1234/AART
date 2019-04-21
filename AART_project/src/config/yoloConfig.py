import os

# jersyTracking.py
defaultModelFolder = os.path.expanduser("~/library/openpose/models/")
darknetCfg = os.path.abspath("../yolov3TrainingSrc/yolov3.cfg")
darnetWeights = os.path.abspath("../yolov3_weights/yolov3_20000.weights")
darknetData = os.path.abspath("../yolov3TrainingSrc/obj.data")

# darknet.py
darknetDir = os.path.abspath("../") + "/"

# obj.data
arr = dict.fromkeys(
	[
		"trainLocation",
		"testLocation",
		"namesLocation",
		"backupLocation"
	],
	None
)
objdataLocation = os.path.abspath("../yolov3TrainingSrc/obj.data")
arr["trainLocation"] = os.path.abspath("../yolov3TrainingSrc/train.txt")
arr["validLocation"] = os.path.abspath("../yolov3TrainingSrc/test.txt")
arr["namesLocation"] = os.path.abspath("../yolov3TrainingSrc/obj.names")
arr["backupLocation"] = os.path.abspath(
	"../yolov3_weights/yolov3_20000.weights"
)


# read-only area
def config():
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
				f.write(
					element.split('=')[0] + '=' + str(
						arr[element.split('=')[0] + "Location"]
					) + '\n'
				)
		f.close()


if __name__ == "__main__":
	config()
