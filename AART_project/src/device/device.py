import wx
import subprocess

import os

from src.media.media import PreviewCamera

class SelectDeviceDialog(wx.Dialog):
	def __init__(self, *args, config, **kwargs):
		super(SelectDeviceDialog, self).__init__(*args, **kwargs)

		self.deviceID_t = -1
		self.deviceID = -1
		self.deviceCheck, self.device = DeviceCheck.deviceQuery()
		self.config = config
		self.config.loadedConfig["fontSize"] -= 5

		# no available web camera device found on current pc
		if self.deviceCheck:
			self.preview = None
			self.InitDeviceUI()
			self.initSize()
		else:
			self.initNoDeviceUI()

	def getMinResolution(self):
		rx = 7680
		ry = 4320
		# get all displays
		displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
		for display in displays:
			tx, ty = display.GetGeometry().GetSize()
			rx = tx if tx < rx else rx
			ry = ty if ty < ry else ry
		return rx, ry

	def initSize(self):
		sx, sy = self.getMinResolution()
		sx = sx * 0.22
		sy = sy * 0.35
		self.SetSize(sx, sy)

	def initNoDeviceUI(self):
		pnl = wx.Panel(self)
		self.SetForegroundColour(
			"white" if self.config.loadedConfig["theme"] == "dark" else "black"
		)
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		vbox = wx.BoxSizer(wx.VERTICAL)

		sbs = wx.StaticBoxSizer(
			wx.StaticBox(
				pnl,
				label='Select web cameras'
			),
			orient=wx.VERTICAL
		)
		temp = wx.StaticText(
			self,
			label="No available web camera device on current pc",
			style=wx.ALIGN_CENTER | wx.CENTER
		)
		temp.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		sbs.Add(temp)
		closeButton = wx.Button(self, label='Ok')
		closeButton.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)

		vbox.Add(
			pnl,
			proportion=1,
			flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER,
			border=1,
		)
		vbox.Add(closeButton, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=1)

		pnl.SetSizer(sbs)
		self.SetSizer(vbox)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Show()

	def InitDeviceUI(self):
		pnl = wx.Panel(self)
		self.SetForegroundColour(
			"white" if self.config.loadedConfig["theme"] == "dark" else "black"
		)
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		# boxsizer declaration
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		sbs = wx.StaticBoxSizer(
			wx.StaticBox(
				pnl,
				label='Select web cameras'
			),
			orient=wx.VERTICAL
		)

		# add valid web camera to wx.RadioButton
		count = 0
		for key, value in self.device.items():
			if count == 0:
				self.deviceID_t = int(value)
			temp = wx.RadioButton(pnl, label=key)
			temp.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"],
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL)
			)
			sbs.Add(temp, flag=wx.ALL | wx.EXPAND)
			count += 1
		self.preview = PreviewCamera(self, self.deviceID_t)

		okButton = wx.Button(self, label='Ok')
		closeButton = wx.Button(self, label='Close')
		okButton.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		closeButton.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)

		hbox.Add(okButton)
		hbox.Add(closeButton, flag=wx.LEFT, border=1)

		vbox.Add(
			pnl,
			proportion=1,
			flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER,
			border=1
		)
		vbox.Add(self.preview, proportion=5, flag=wx.ALL | wx.EXPAND, border=1)
		vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=1)

		pnl.SetSizer(sbs)
		self.SetSizer(vbox)
		self.Bind(
			wx.EVT_RADIOBUTTON,
			lambda event, temp=self.preview: self.onSelect(event, temp)
		)

		# event biding
		okButton.Bind(wx.EVT_BUTTON, self.onOk)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Show()

	def onSelect(self, event, pnl):
		self.deviceID_t = int(self.device[event.GetEventObject().GetLabel()])
		# passing device id temp to preview for update
		self.preview.deviceIDT = self.deviceID_t

	def onOk(self, event):
		self.deviceID = self.deviceID_t
		self.preview.capture.release()
		self.onClose(event)

	def onClose(self, event):
		self.preview.capture.release()
		self.Destroy()

class DeviceCheck:
	@staticmethod
	def getId(idt):
		ids = dict()
		repeatMapping = dict()

		for element in idt.split("|"):
			id, index = element.split("_")

			if id == " ." or id == " ..":
				continue

			if ":" not in str(id):
				ids[id] = index
			else:
				first = str(id).split(":")[0]
				second = str(id).split(":")[1]
				repeat = str(id).split(":")[2]

				currentId = "{}:{}".format(first, second)

				repeatMapping[currentId] = repeatMapping.get(currentId, 0) + 1
				ids["{}:{}".format(currentId, repeat)] = index

		# construct mapping count
		repeatMappingCount = {x: 0 for x in repeatMapping.keys()}
		return ids, repeatMapping, repeatMappingCount

	@staticmethod
	def getUsb(usbt):
		usbs = dict()

		for element in usbt.split("|"):
			id, name = element.split(" ", 1)
			usbs[id] = name
		return usbs

	@staticmethod
	def checkV4l():
		p = subprocess.Popen(
			"ls -al /dev/ | grep v4l",
			shell=True,
			stdout=subprocess.PIPE
		)
		out, err = p.communicate()

		# out will be bytes literal, thus in comparison need to use decode
		return True if not out.decode() == "" else False

	@staticmethod
	def deviceQuery():
		retDeviceCheck = False
		retDevice = dict()

		path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

		if not DeviceCheck.checkV4l():
			pass
		else:
			subprocess.call(["chmod +x {}/fetch.sh".format(path)], shell=True)
			p = subprocess.Popen(
				"{}/fetch.sh".format(path),
				shell=True,
				stdout=subprocess.PIPE,
				executable="/bin/bash"
			)
			output, err = p.communicate()
			errorcode = p.returncode

			if errorcode == 0:
				output = str(output)[2:-1]
				idt, usbt = output.split("@")
				ids, repeatMapping, repeatMappingCount = DeviceCheck.getId(idt)
				usbs = DeviceCheck.getUsb(usbt)
				devices = dict()

				# id name mapping
				for id, index in ids.items():
					if ":" in id:
						twoId = "{}:{}".format(str(id).split(":")[0], str(id).split(":")[1])

						if twoId in usbs:
							if repeatMapping[twoId] <= 1:
								devices["{}".format(usbs[twoId])] = index
							else:
								devices["{} [ {} ]".format(
									usbs[twoId],
									repeatMappingCount[twoId] + 1
								)] = index
							repeatMappingCount[twoId] += 1
					else:
						if id in usbs:
							devices[usbs[id]] = index

				diff = set(ids.values()) - set(devices.values())
				if len(diff) != 0:
					id = diff.pop()
					devices["Build in web camera"] = id
			retDeviceCheck = True
			retDevice = devices

		return retDeviceCheck, retDevice
