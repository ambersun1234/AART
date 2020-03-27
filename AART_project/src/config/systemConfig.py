import os
import json

import gettext

class systemConfig:
	def __init__(self, path):
		self.path = "{}/systemConfig.json".format(os.path.dirname(path))

		temp = list()
		self.loadedConfig = {
			"language": "en",
			"fontSize": 17,
			"theme": "dark",
			"recent": temp,
			"colorBg": "#4F5D75",
			"colorTitle": "#333138",
			"colorText": "#F5F0EB"
		}

		# set language
		lang = "tw" if self.loadedConfig["language"] == "tw" else "en"
		t = gettext.translation(
			"base",
			localedir="./locales",
			languages=[lang]
		)
		t.install()
		global _
		_ = t.gettext

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
				print(_("config file not found"))
		else:
			# config.json not found
			# write default config settings to .json file
			try:
				with open(self.path, "w") as file:
					json.dump(self.loadedConfig, file)

			except FileNotFoundError as e:
				print(_("Error occurred"))

	def save(self):
		try:
			with open(self.path, "w") as file:
				json.dump(self.loadedConfig, file)

		except FileNotFoundError as e:
			print(_("Error occurred"))

	def storeLang(self, lang):
		self.loadedConfig["language"] = lang

	def storePath(self, path):
		if path not in self.loadedConfig["recent"]:
			self.loadedConfig["recent"].append(path)
