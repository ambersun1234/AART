import wx
import wx.lib.scrolledpanel as scrolled
import os

class welcomeGuide(wx.Dialog):
	def __init__(self, *args, path, **kwargs):
		super(welcomeGuide, self).__init__(*args, **kwargs)

		self.logo = wx.Image("{}/logo.png".format(os.path.dirname(path)))
		self.bmp = None
		self.sp = None

		self.initUI()
		self.Show()

	def initUI(self):
		self.initImgSize()

		self.sp = self.initScrolledPanel()

		spBox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)

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

		self.SetBackgroundColour("gray")
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
