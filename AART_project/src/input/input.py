import wx

import gettext

class InputPanel(wx.Panel):
	def __init__(self, parent, size, config, nn):
		wx.Panel.__init__(self, parent, size=size)

		self.field = dict()
		for i in range(0, 3):
			# self.field.append(wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER))
			self.field[i] = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
			self.field[i].SetValue("")
		# textCtrl must contain wx.TE_PROCESS_ENTER => event: EVT_TEXT_ENTER

		self.nn = nn
		self.config = config
		self.input = dict()
		# store user input

		# set language
		lang = "tw" if self.config.loadedConfig["language"] == "tw" else "en"
		t = gettext.translation(
			"base",
			localedir="./locales",
			languages=[lang]
		)
		t.install()
		global _
		_ = t.gettext

		self.initUI()

	def initUI(self):
		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)

		title = wx.StaticText(self, label=_(" Athlete trace: "))
		title.SetForegroundColour(
			self.config.loadedConfig["colorText"]
		)
		title.SetBackgroundColour(
			self.config.loadedConfig["colorTitle"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		title.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"] + 5,
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		titleLine = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
		vbox.Add(title, flag=wx.ALL | wx.EXPAND)
		vbox.Add(titleLine, flag=wx.EXPAND | wx.ALL)
		vbox.AddSpacer(5)

		sta = list()
		for index in range(1, 4):
			sta.append(
				wx.StaticText(
					self,
					label="   {}{}: ".format(_("Athlete"), index)
				)
			)

		for element in sta:
			element.SetForegroundColour(
				self.config.loadedConfig["colorText"]
			)
			element.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"],
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL
			))

		# add static text and field
		for index, item, box in zip(
			range(0, 3), sta,
			[hbox1, hbox2, hbox3]):
			box.Add(item, border=5)
			box.Add(self.field[index], border=5, flag=wx.EXPAND | wx.ALL, proportion=3)

			self.field[index].Bind(
				wx.EVT_TEXT_ENTER,
				lambda event,
				temp=index: self.onEnter(event, temp)
			)

			# button ok
			ok = wx.Button(self, label=_("Ok"), size=(60, 30))
			ok.SetFont(wx.Font(
				11,
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.FONTWEIGHT_BOLD
			))
			ok.SetForegroundColour("green")
			box.Add(ok, flag=wx.ALL, border=5)
			ok.Bind(
				wx.EVT_BUTTON,
				lambda event,
				temp=index: self.onEnter(event, temp)
			)

			# button close
			close = wx.Button(self, label=_("Clear"), size=(60, 30))
			close.SetFont(wx.Font(
				11,
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.FONTWEIGHT_BOLD
			))
			close.SetForegroundColour("red")
			box.Add(close, flag=wx.ALL, border=5)
			close.Bind(
				wx.EVT_BUTTON,
				lambda event,
				temp=index: self.onClear(event, temp)
			)

			# add to vertical
			vbox.Add(box, flag=wx.EXPAND | wx.ALL)

		self.SetSizer(vbox)
		self.SetBackgroundColour(
			self.config.loadedConfig["colorBg"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		self.Show()

	def onClear(self, event, buttonLabel):
		self.input.pop(buttonLabel, "")
		self.field[buttonLabel].SetValue("")
		# pass dict to neural network
		self.nn._idict = self.input
		if not self.input:
			self.nn._imode = 0

	def onEnter(self, event, buttonLabel):
		input_t = self.field[buttonLabel].GetValue()

		if self.inputCheck(input_t):
			self.input[buttonLabel] = input_t
			# pass dict to neural network
			self.nn._idict = self.input
			self.nn._imode = 1
		else:
			self.field[buttonLabel].SetValue("")
			self.input.pop(buttonLabel, None)
			if not self.input:
				self.nn._imode = 0

	def inputCheck(self, input):
		return str(input).isdigit()

	def inputReinit(self):
		self.input = dict()
		self.nn._imode = 0
		for i in range(0, 3):
			self.field[i].SetValue("")
