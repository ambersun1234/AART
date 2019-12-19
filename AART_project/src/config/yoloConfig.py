import os

class number():
	def __init__(self):
		self.defaultModelFolder = os.path.expanduser("~/library/openpose/models/")
		self.darknetCfg = os.path.abspath("../yolov3TrainingSrc/yolov3.cfg")
		self.darnetWeights = os.path.abspath("../yolov3_weights/yolov3_170000.weights")
		self.darknetData = os.path.abspath("../yolov3TrainingSrc/obj.data")

		# darknet.py
		self.darknetDir = '/home/aart/library/darknet/'

		# obj.data
		self.arr = dict.fromkeys(
			[
				"trainLocation",
				"testLocation",
				"namesLocation",
				"backupLocation"
			],
			None
		)
		self.objdataLocation = os.path.abspath("../yolov3TrainingSrc/obj.data")
		self.arr["trainLocation"] = os.path.abspath("../yolov3TrainingSrc/train.txt")
		self.arr["validLocation"] = os.path.abspath("../yolov3TrainingSrc/test.txt")
		self.arr["namesLocation"] = os.path.abspath("../yolov3TrainingSrc/obj.names")
		self.arr["backupLocation"] = os.path.abspath(
			"../yolov3_weights/yolov3_40000.weights"
		)

	def config(self):
		lines = []
		try:
			with open(self.objdataLocation, "r") as fp:
				lines = fp.readlines()
				fp.close()
		except IOError:
			print(self.objdataLocation + " not found")

		with open(self.objdataLocation, "w") as f:
			count = 1
			for element in lines:
				if count == 1:
					f.write(element)
					count += 1
				else:
					f.write(
						element.split('=')[0] + '=' + str(
							self.arr[element.split('=')[0] + "Location"]
						) + '\n'
					)
			f.close()

class number20():
	def __init__(self):
		self.defaultModelFolder = os.path.expanduser("~/library/openpose/models/")
		self.darknetCfg = os.path.abspath("../yolov3TrainingSrc/number20/yolov3.cfg")
		self.darnetWeights = os.path.abspath("../yolov3_weights/yolov3_100002.weights")
		self.darknetData = os.path.abspath("../yolov3TrainingSrc/number20/obj.data")

		# darknet.py
		self.darknetDir = '/home/louisme/library/darknet/'

		# obj.data
		self.arr = dict.fromkeys(
			[
				"trainLocation",
				"testLocation",
				"namesLocation",
				"backupLocation"
			],
			None
		)
		self.objdataLocation = os.path.abspath("../yolov3TrainingSrc/number20/obj.data")
		self.arr["trainLocation"] = os.path.abspath("../yolov3TrainingSrc/number20/train.txt")
		self.arr["validLocation"] = os.path.abspath("../yolov3TrainingSrc/number20/test.txt")
		self.arr["namesLocation"] = os.path.abspath("../yolov3TrainingSrc/number20/obj.names")
		self.arr["backupLocation"] = os.path.abspath(
			"../yolov3_weights/yolov3_100002"
			".weights"
		)

	# read-only area
	def config(self):
		lines = []
		try:
			with open(self.objdataLocation, "r") as fp:
				lines = fp.readlines()
				fp.close()
		except IOError:
			print(self.objdataLocation + " not found")

		with open(self.objdataLocation, "w") as f:
			count = 1
			for element in lines:
				if count == 1:
					f.write(element)
					count += 1
				else:
					f.write(
						element.split('=')[0] + '=' + str(
							self.arr[element.split('=')[0] + "Location"]
						) + '\n'
					)
			f.close()
