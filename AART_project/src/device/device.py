import wx
import subprocess

class SelectDeviceDialog(wx.Dialog):
	def __init__(self, *args, **kwargs):
		super(SelectDeviceDialog, self).__init__(*args, **kwargs)

		self.deviceID = -1
		self.device = DeviceCheck.deviceQuery()
		self.InitUI()

	def InitUI(self):
		pnl = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		sb = wx.StaticBox(pnl, label='Colors')
		sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

		for key, value in self.device.items():
			sbs.Add(wx.RadioButton(pnl, label=key))

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		okButton = wx.Button(self, label='Ok')
		closeButton = wx.Button(self, label='Close')
		hbox.Add(okButton)
		hbox.Add(closeButton, flag=wx.LEFT, border=5)

		vbox.Add(pnl, proportion=1,
                    flag=wx.ALL | wx.EXPAND, border=5)
		vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

		self.SetSizer(vbox)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSelect)

		okButton.Bind(wx.EVT_RADIOBUTTON, self.onClose)
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)

	def onSelect(self, event):
		self.deviceID = int(self.device[event.GetEventObject().GetLabel()])
		print(self.deviceID)

	def onClose(self, event):
		self.Destroy()

class DeviceCheck:
	@staticmethod
	def deviceQuery():
		subprocess.call(["chmod +x ./fetch.sh"], shell=True)
		p = subprocess.Popen("./fetch.sh", shell=True, stdout=subprocess.PIPE, executable="/bin/bash")
		output, err = p.communicate()
		errorcode = p.returncode

		if errorcode == 0:
			output = str(output)[2:-1]
			idt, usbt = output.split("@")
			ids = dict()
			usbs = dict()
			devices = dict()

			# fetch id
			for element in idt.split("|"):
				id, index = element.split("_")
				ids[id] = index
			for element in usbt.split("|"):
				id, name = element.split(" ", 1)
				usbs[id] = name

			# id name mapping
			for id, index in ids.items():
				if id in usbs:
					devices[usbs[id]] = index
			diff = set(ids.values()) - set(devices.values())

			if len(diff) != 0:
				id = diff.pop()
				devices["Build in web camera"] = id

		return devices
