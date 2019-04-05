import wx

class outputTextPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)

		self.text = {"person1": "pitch", "person2": "layup"}
		self.config = config
		# self.text = dict()
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"gray" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		vbox = wx.BoxSizer(wx.VERTICAL)

		title = wx.StaticText(self, label="Athlete action: ")
		title.SetForegroundColour(
			"white" if self.config.loadedConfig["theme"] == "dark" else "black"
		)
		title.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		vbox.AddSpacer(5)
		vbox.Add(title)
		vbox.AddSpacer(5)
		titleLine = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
		vbox.Add(titleLine, flag=wx.ALL | wx.EXPAND)
		vbox.AddSpacer(5)

		for key, value in self.text.items():
			temp = wx.StaticText(self, label="{}: {}".format(key, value))
			temp.SetForegroundColour(
				"white" if self.config.loadedConfig["theme"] == "dark" else "black"
			)
			temp.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"],
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL)
			)

			vbox.Add(temp)

		self.SetSizer(vbox)
		self.Show()

class outputPicPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"gray" if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		vbox = wx.BoxSizer(wx.VERTICAL)
		hboxD = wx.BoxSizer(wx.HORIZONTAL)

		title = wx.StaticText(self, label="Athlete picture")
		title.SetForegroundColour(
			"white" if self.config.loadedConfig["theme"] == "dark" else "black"
		)
		title.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		titleLine = wx.StaticLine(self, style=wx.LI_HORIZONTAL)

		vbox.AddSpacer(5)
		vbox.Add(title)
		vbox.AddSpacer(5)
		vbox.Add(titleLine, flag=wx.EXPAND | wx.ALL)
		vbox.AddSpacer(5)
		vbox.Add(hboxD)

		self.SetSizer(vbox)
		self.Show()
