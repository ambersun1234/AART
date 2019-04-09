import wx
import wx.lib.scrolledpanel as scrolled
import os

class WelcomeGuide(wx.Dialog):
	def __init__(self, *args, path, config, **kwargs):
		super(WelcomeGuide, self).__init__(*args, **kwargs)

		self.logo = wx.Image("{}/logo.png".format(os.path.dirname(path)))
		self.bmp = None
		self.sp = None
		self.config = config

		self.initUI()
		self.Show()

	def initUI(self):
		self.initImgSize()

		self.sp = self.initScrolledPanel()

		spBox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)

		w, h = self.GetSize()
		text = wx.StaticText(self, label="Recent files", style=wx.ALIGN_CENTER)

		if self.config.loadedConfig["theme"] == "dark":
			text.SetForegroundColour("white")
			text.SetBackgroundColour("#666666")
		else:
			text.SetForegroundColour("black")
			text.SetBackgroundColour("#e2e2e2")

		text.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		text.SetMinSize((w - h - 100, self.config.loadedConfig["fontSize"] + 7))
		spBox.Add(text, flag=wx.EXPAND | wx.ALL)

		for i in range(1, 30):
			spBox.Add(wx.Button(self.sp, label="lala{}".format(i)))

		self.sp.SetSizer(spBox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		hbox.Add(self.sp, flag=wx.ALIGN_LEFT | wx.ALL)
		hbox.Add(
			wx.StaticBitmap(self, wx.ID_ANY, self.bmp),
			flag=wx.ALIGN_RIGHT
		)
		vbox.Add(hbox, flag=wx.ALL | wx.EXPAND)

		if self.config.loadedConfig["theme"] == "dark":
			self.SetBackgroundColour("#4c4c4c")
		else:
			self.SetBackgroundColour("white")
		self.SetSizer(vbox)

	def initScrolledPanel(self):
		width, height = self.GetSize()
		temp = scrolled.ScrolledPanel(
			self,
			size=(width - height, height),
			name="Recent file",
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)
		return temp

	def initImgSize(self):
		width, height = self.GetSize()
		self.imgScale(height, height)

	def imgScale(self, width, height):
		self.logo = self.logo.Scale(width, height, quality=wx.IMAGE_QUALITY_HIGH)
		self.bmp = self.logo.ConvertToBitmap()
