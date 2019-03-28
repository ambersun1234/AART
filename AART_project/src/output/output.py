import wx

class outputTextPanel(wx.Panel):
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent, size=size)

		self.text = {"person1": "pitch", "person2": "layup"}
		# self.text = dict()
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour("gray")

		vbox = wx.BoxSizer(wx.VERTICAL)

		for key, value in self.text.items():
			temp = wx.StaticText(self, label="{}: {}".format(key, value))
			temp.SetForegroundColour((255, 255, 255))
			temp.SetFont(wx.Font(
				14,
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL)
			)

			vbox.Add(temp)

		self.SetSizer(vbox)
		self.Show()

class outputPicPanel(wx.Panel):
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent, size=size)
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour("gray")
		self.Show()
