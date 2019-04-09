import os
import json

class Config:
	def __init__(self, path):
		self.path = "{}/config.json".format(os.path.dirname(path))

		temp = list()
		self.loadedConfig = {
			"language": "eng",
			"fontSize": 14,
			"theme": "dark",
			"recent": temp
		}

		self.load()

	def load(self):
		if os.path.exists(self.path):
			try:
				with open(self.path, "r") as file:
					# load previous config
					data = json.load(file)
					for element in data:
						self.loadedConfig[element] = data[element]

			except FileNotFoundError as e:
				print("config file not found")
		else:
			# config.json not found
			# write default config settings to .json file
			try:
				with open(self.path, "w") as file:
					json.dump(self.loadedConfig, file)

			except FileNotFoundError as e:
				print("Error occurred")

	def save(self):
		try:
			with open(self.path, "w") as file:
				json.dump(self.loadedConfig, file)

		except FileNotFoundError as e:
			print("Error occurred")

	def storePath(self, path):
		self.loadedConfig["recent"].append(path)
