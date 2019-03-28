import wx

class InputPanel(wx.Panel):
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent, size=size)

		self.field1 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.field2 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.field3 = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		# textCtrl must contain wx.TE_PROCESS_ENTER => event: EVT_TEXT_ENTER

		self.input = dict()
		# store user input

		self.initUI()

	def initUI(self):
		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)

		t1 = wx.StaticText(self, label="person1: ")
		t2 = wx.StaticText(self, label="person2: ")
		t3 = wx.StaticText(self, label="person3: ")

		for element in [t1, t2, t3]:
			element.SetForegroundColour((255, 255, 255))
			element.SetFont(wx.Font(
				14,
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL
			))

		hbox1.Add(t1, border=5)
		hbox2.Add(t2, border=5)
		hbox3.Add(t3, border=5)

		hbox1.Add(self.field1, flag=wx.LEFT | wx.CENTER, border=5)
		hbox2.Add(self.field2, flag=wx.LEFT | wx.CENTER, border=5)
		hbox3.Add(self.field3, flag=wx.LEFT | wx.CENTER, border=5)

		vbox.Add(hbox1)
		vbox.Add(hbox2)
		vbox.Add(hbox3)

		self.field1.Bind(
			wx.EVT_TEXT_ENTER,
			lambda event,
			temp=0: self.onEnter(event, temp)
		)
		self.field2.Bind(
			wx.EVT_TEXT_ENTER,
			lambda event,
			temp=1: self.onEnter(event, temp)
		)
		self.field3.Bind(
			wx.EVT_TEXT_ENTER,
			lambda event,
			temp=2: self.onEnter(event, temp)
		)

		self.SetSizer(vbox)
		self.SetBackgroundColour("gray")
		self.Show()

	def onEnter(self, event, buttonLabel):
		self.input[buttonLabel] = event.GetString() \
			if self.inputCheck(event.GetString()) else ""
		print(self.input)

	def inputCheck(self, input):
		return str(input).isdigit()
