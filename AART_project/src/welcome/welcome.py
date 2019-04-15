import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.stattext as st
import os

import gettext

class WelcomeGuide(wx.Dialog):
	def __init__(self, *args, path, config, **kwargs):
		super(WelcomeGuide, self).__init__(*args, **kwargs)

		self.logo = wx.Image("{}/logo.png".format(os.path.dirname(path)))
		self.bmp = None
		self.sp = None
		self.config = config
		self.path = ""

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
		self.Show()

	def initUI(self):
		self.initImgSize()

		self.sp = self.initScrolledPanel()

		spBox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox = wx.BoxSizer(wx.VERTICAL)

		if self.config.loadedConfig["theme"] == "dark":
			self.SetBackgroundColour("#4c4c4c")
		else:
			self.SetBackgroundColour("white")

		# check do have recent files
		if self.config.loadedConfig["recent"]:
			for recentfull in self.config.loadedConfig["recent"]:
				recent = os.path.basename(recentfull)
				temp = st.GenStaticText(self.sp, label="   {}".format(recent))
				temp2 = st.GenStaticText(self.sp, label="   {}".format(recentfull))

				# left mouse button click event
				temp.Bind(
					wx.EVT_LEFT_DOWN,
					lambda event,
					arg=recentfull: self.onClick(event, arg)
				)
				temp2.Bind(
					wx.EVT_LEFT_DOWN,
					lambda event,
					arg=recentfull: self.onClick(event, arg)
				)

				# mouse enter event
				temp.Bind(
					wx.EVT_ENTER_WINDOW,
					lambda event,
					arg1=temp,
					arg2=temp2: self.onEnter(event, arg1, arg2)
				)
				temp2.Bind(
					wx.EVT_ENTER_WINDOW,
					lambda event,
					arg1=temp2,
					arg2=temp: self.onEnter(event, arg1, arg2)
				)

				# mouse leave event
				temp.Bind(
					wx.EVT_LEAVE_WINDOW,
					lambda event,
					arg1=temp,
					arg2=temp2: self.onLeave(event, arg1, arg2)
				)
				temp2.Bind(
					wx.EVT_LEAVE_WINDOW,
					lambda event,
					arg1=temp2,
					arg2=temp: self.onLeave(event, arg1, arg2)
				)

				tvbox = wx.BoxSizer(wx.VERTICAL)
				tvbox.Add(temp, flag=wx.EXPAND)
				tvbox.Add(temp2, flag=wx.EXPAND)

				if self.config.loadedConfig["theme"] == "dark":
					temp.SetForegroundColour("white")
					temp2.SetForegroundColour("#dbdbdb")
				else:
					temp.SetForegroundColour("black")
					temp2.SetForegroundColour("black")

				temp.SetFont(wx.Font(
					self.config.loadedConfig["fontSize"] - 3,
					family=wx.DEFAULT,
					style=wx.NORMAL,
					weight=wx.NORMAL)
				)
				temp2.SetFont(wx.Font(
					self.config.loadedConfig["fontSize"] - 5,
					family=wx.DEFAULT,
					style=wx.NORMAL,
					weight=wx.NORMAL)
				)

				# add space
				spBox.AddSpacer(5)
				spBox.Add(tvbox, flag=wx.EXPAND)
		else:
			# no recent files
			text = wx.StaticText(self.sp, label=_("   No recent files"))
			if self.config.loadedConfig["theme"] == "dark":
				text.SetForegroundColour("white")
			else:
				text.SetForegroundColour("black")
				text.SetBackgroundColour("#e2e2e2")
			text.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"] - 3,
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL)
			)
			# add space
			spBox.AddSpacer(5)
			spBox.Add(text, flag=wx.EXPAND)

		self.sp.SetSizer(spBox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		hbox.Add(self.sp, flag=wx.ALIGN_LEFT | wx.ALL)
		hbox.Add(
			wx.StaticBitmap(self, wx.ID_ANY, self.bmp),
			flag=wx.ALIGN_RIGHT
		)
		vbox.Add(hbox, flag=wx.ALL | wx.EXPAND)

		self.SetSizer(vbox)

	def onEnter(self, event, text, text2):
		text.SetBackgroundColour("#f75b25")
		text2.SetBackgroundColour("#f75b25")

	def onLeave(self, event, text, text2):
		if self.config.loadedConfig["theme"] == "dark":
			text.SetBackgroundColour("#4c4c4c")
			text2.SetBackgroundColour("#4c4c4c")
		else:
			text.SetBackgroundColour("white")
			text2.SetBackgroundColour("white")

	def onClick(self, event, path):
		if not os.path.exists(path):
			wx.MessageBox(
				_("File not found."),
				_("ERROR"),
				wx.ICON_ERROR | wx.OK
			)
		else:
			self.path = path
			self.Destroy()

	def initScrolledPanel(self):
		width, height = self.GetSize()
		temp = scrolled.ScrolledPanel(
			self,
			size=(width - height, height),
			name=_("Recent file"),
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)
		return temp

	def initImgSize(self):
		width, height = self.GetSize()
		self.imgScale(height, height)

	def imgScale(self, width, height):
		self.logo = self.logo.Scale(width, height, quality=wx.IMAGE_QUALITY_HIGH)
		self.bmp = self.logo.ConvertToBitmap()
