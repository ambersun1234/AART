import wx
import subprocess

class SelectDeviceDialog(wx.Dialog):
	def __init__(self, *args, **kwargs):
		super(SelectDeviceDialog, self).__init__(*args, **kwargs)

		self.deviceID_t = -1
		self.deviceID = -1
		self.device = DeviceCheck.deviceQuery()
		self.InitUI()

	def InitUI(self):
		pnl = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		sb = wx.StaticBox(pnl, label='Select web cameras')
		sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

		for key, value in self.device.items():
			temp = wx.RadioButton(pnl, label=key)
			sbs.Add(temp)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		okButton = wx.Button(self, label='Ok')
		closeButton = wx.Button(self, label='Close')
		hbox.Add(okButton)
		hbox.Add(closeButton, flag=wx.LEFT, border=5)

		vbox.Add(
			pnl,
			proportion=1,
			flag=wx.ALL | wx.EXPAND,
			border=5
		)
		vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)

		pnl.SetSizer(sbs)
		self.SetSizer(vbox)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelect)

		okButton.Bind(wx.EVT_RADIOBUTTON, self.onOk)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)

	def onSelect(self, event):
		self.deviceID_t = int(self.device[event.GetEventObject().GetLabel()])
		print(self.deviceID_t)

	def onOk(self):
		self.deviceID = self.deviceID_t

	def onClose(self, event):
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
	def deviceQuery():
		subprocess.call(["chmod +x ./fetch.sh"], shell=True)
		p = subprocess.Popen(
			"./fetch.sh",
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

		return {k: v for k, v in sorted(devices.items(), key=lambda x: x[1])}
