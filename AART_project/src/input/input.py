import wx

import gettext
t = gettext.translation(
	"base",
	localedir=".",
	languages=["tw"]
)
t.install()
_ = t.gettext()

class InputPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)

		self.field = dict()
		for i in range(0, 3):
			# self.field.append(wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER))
			self.field[i] = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
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

		title = wx.StaticText(self, label=_(" Athlete trace: "))
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
			sta.append(wx.StaticText(self, label="   Athlete{}: ".format(_(index))))

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
			ok.SetForegroundColour("green")
			box.Add(ok, flag=wx.ALL, border=5)
			ok.Bind(
				wx.EVT_BUTTON,
				lambda event,
				temp=index: self.onEnter(event, temp)
			)

			# button close
			close = wx.Button(self, label=_("Clear"), size=(60, 30))
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
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		self.Show()

	def onClear(self, event, buttonLabel):
		self.input[buttonLabel] = ""
		print(self.input)

	def onEnter(self, event, buttonLabel):
		input_t = self.field[buttonLabel].GetValue()

		self.input[buttonLabel] = input_t \
			if self.inputCheck(input_t) \
			else self.input.get(buttonLabel, "")
		print(self.input)

	def inputCheck(self, input):
		return str(input).isdigit()
