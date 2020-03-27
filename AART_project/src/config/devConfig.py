import os
import configparser
import sys

class devConfig():
	def __init__(self):
		tmp = os.path.abspath(__file__)
		for i in range(2):
			tmp = os.path.dirname(tmp)
		self.rootPath = tmp
		self.config = configparser.ConfigParser()

		# default path
		self.extend = {
			"cfg": "yolov3.cfg", "weights": "yolov3_170000.weights",
			"data": "obj.data", "train": "train.txt",
			"test": "test.txt", "names": "obj.names",
			"backup": "bp.weights"
		}

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
		self.map = {
			"trainLocation": self.extend["train"],
			"validLocation": self.extend["test"],
			"namesLocation": self.extend["names"],
			"backupLocation": self.extend["backup"]
		}

		# read from ini
		self._ini_darknet_src = None
		self._ini_darknet_run = None
		self._ini_openpose_model = None

		self.load()

	def load(self):
		targetFile = "{}/devconfig.ini".format(self.rootPath)
		rt = False

		if not os.path.isfile(targetFile):
			sys.exit(1)

		try:
			self.config.read(targetFile)
			self._ini_darknet_src    = self.config["darknet"]["srcLocation"]
			self._ini_darknet_run    = self.config["darknet"]["runLocation"]
			self._ini_openpose_model = self.config["openpose"]["modelLocation"]
		except KeyError as e:
			rt = True
		except ValueError as e:
			rt = True
		finally:
			if None or "" in \
				(self._ini_darknet_run, self._ini_darknet_src, self._ini_openpose_model):
				rt = True

		if rt:
			print("{} not found. terminate".format(targetFile))
			sys.exit(1)
		else:

			for key, value in self.map.items():
				self.arr[key] = "{}/{}".format(self.rootPath, value)

			for key, value in self.extend.items():
				self.extend[key] = self._ini_darknet_src + value

	def write(self):
		lines = []
		tmpPath = "{}/{}".format(
			self._ini_darknet_src,
			self.extend["data"]
		)
		if not os.path.isfile(tmpPath):
			print(tmpPath + " not found")

		with open(tmpPath, "w") as f:
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
