import wx

class InputPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)

		self.field1 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.field2 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.field3 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		# textCtrl must contain wx.TE_PROCESS_ENTER => event: EVT_TEXT_ENTER

		self.config = config
		self.input = dict()
		# store user input

		self.initUI()

	def initUI(self):
		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)

		title = wx.StaticText(self, label="Athlete trace: ")
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

		sta = list()
		for index in range(1, 4):
			sta.append(wx.StaticText(self, label="person{}: ".format(index)))

		for element in sta:
			element.SetForegroundColour(
				"white" if self.config.loadedConfig["theme"] == "dark" else "black"
			)
			element.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"],
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL
			))

		for item, box, field in zip(
			sta, [hbox1, hbox2, hbox3],
			[self.field1, self.field2, self.field3]):
			box.Add(item, border=5)
			box.Add(field, border=5, flag=wx.EXPAND)
			vbox.Add(box, flag=wx.EXPAND | wx.ALL)

		for index, field in zip(
			range(0, 3),
			[self.field1, self.field2, self.field3]):
			field.Bind(
				wx.EVT_TEXT_ENTER,
				lambda event,
				temp=index: self.onEnter(event, temp)
			)

		self.SetSizer(vbox)
		self.SetBackgroundColour(
			"gray" if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		self.Show()

	def onEnter(self, event, buttonLabel):
		self.input[buttonLabel] = event.GetString() \
			if self.inputCheck(event.GetString()) else ""
		print(self.input)

	def inputCheck(self, input):
		return str(input).isdigit()
