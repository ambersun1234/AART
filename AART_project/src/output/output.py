import wx
import wx.lib.scrolledpanel as scrolled
from PIL import Image
import math
import cv2
import collections

import gettext

class OutputTextPanel(wx.Panel):
	def __init__(self, parent, size, config, nn):
		wx.Panel.__init__(self, parent, size=size)

		self.text = {"empty": "empty"}
		self.nn = nn
		self.config = config
		self.sp = None
		self.spbox = wx.BoxSizer(wx.VERTICAL)
		self.currentWidth = self.GetSize()[1]

		# dynamically get text from LSTM
		self.fps = 20
		self.timer = wx.Timer(self)
		self.timer.Start(1000. / self.fps)

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

	def onTimer(self, event):
		if self.nn._odict:
			od = collections.OrderedDict(
				sorted(
					self.nn._odict.items(),
					key=lambda x: int(x[0])
				)
			)
			self.spbox.Clear(True)
			pos = 0
			for number, posture in od.items():
				text = wx.StaticText(
					self.sp,
					label="   {} {}: {}".format(_("Athlete"), number, _(posture)),
					pos=(0, pos),
					size=(self.currentWidth, self.config.loadedConfig["fontSize"])
				)
				text.SetForegroundColour(self.config.loadedConfig["colorText"])
				text.SetFont(
					wx.Font(
						self.config.loadedConfig["fontSize"],
						family=wx.DEFAULT,
						style=wx.NORMAL,
						weight=wx.NORMAL
					)
				)
				self.spbox.Add(text, flag=wx.EXPAND | wx.ALL, proportion=5)
				pos += 30

		self.sp.SetSizer(self.spbox)

	def initUI(self):
		self.SetBackgroundColour(
			self.config.loadedConfig["colorBg"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		self.sp = scrolled.ScrolledPanel(
			self,
			name=_("out"),
			size=self.GetSize(),
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)

		vbox = wx.BoxSizer(wx.VERTICAL)

		title = wx.StaticText(self, label=_(" Athlete action: "))
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
		titleLine = wx.StaticLine(
			self,
			style=wx.LI_HORIZONTAL
		)
		vbox.Add(title, flag=wx.ALL | wx.EXPAND)
		vbox.Add(titleLine, flag=wx.ALL | wx.EXPAND)
		vbox.AddSpacer(5)

		# dynamically change output text
		self.Bind(wx.EVT_TIMER, self.onTimer)

		check = False
		for key, value in self.text.items():
			if not key == "empty" or not value == "empty":
				temp = wx.StaticText(
					self.sp,
					label="   {} {}: {}".format(_("Athlete"), _(key), _(value)),
					size=(-1, self.config.loadedConfig["fontSize"] + 17)
				)
			else:
				temp = wx.StaticText(
					self.sp,
					label="",
					size=(-1, self.config.loadedConfig["fontSize"] + 17)
				)
			temp.SetForegroundColour(
				self.config.loadedConfig["colorText"]
			)
			temp.SetFont(wx.Font(
				self.config.loadedConfig["fontSize"],
				family=wx.DEFAULT,
				style=wx.NORMAL,
				weight=wx.NORMAL)
			)
			if check:
				self.spbox.AddSpacer(5)
			else:
				check = True
			self.spbox.Add(temp, flag=wx.EXPAND | wx.ALL)

		self.sp.SetSizer(self.spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp, flag=wx.ALL)

		self.SetSizer(vbox)
		self.Show()

class OutputPicPanel(wx.Panel):
	def __init__(self, parent, size, config, nn):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.sp = None
		self.spbox = wx.BoxSizer(wx.HORIZONTAL)
		self.nn = nn

		self.w, self.h = self.GetSize()

		# dynamically get image from LSTM
		self.fps = 20
		self.timer = wx.Timer(self)
		self.timer.Start(1000. / self.fps)
		# binding event below, dynamic width and height

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

	def onTimer(self, event):
		offset = 40
		if self.nn._oimg:
			od = collections.OrderedDict(
				sorted(
					self.nn._oimg.items(),
					key=lambda x: int(x[0])
				)
			)
			self.spbox.Clear(True)
			posx = 0
			count = math.floor(self.w * 0.14)
			for number, img in od.items():
				tsizer = wx.BoxSizer(wx.VERTICAL)

				# make bmp
				img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
				img = cv2.resize(
					img,
					(count, self.h - offset),
					interpolation=cv2.INTER_CUBIC
				)
				img = Image.fromarray(img, "RGB")
				w, h = img.size
				temp = wx.Bitmap.FromBuffer(w, h, img.tobytes())

				# make text
				text = wx.StaticText(
					self.sp,
					label="   {}: {}".format(_("Athlete"), number),
					pos=(posx, 0),
					size=(self.w * 0.14, 10)
				)
				text.SetForegroundColour(self.config.loadedConfig["colorText"])
				text.SetBackgroundColour("black")
				text.SetFont(
					wx.Font(
						self.config.loadedConfig["fontSize"] - 2,
						family=wx.DEFAULT,
						style=wx.NORMAL,
						weight=wx.NORMAL
					)
				)

				# make sizer
				tsizer.Add(
					text,
					flag=wx.CENTER | wx.ALIGN_CENTER
				)
				tsizer.Add(
					wx.StaticBitmap(
						self.sp,
						bitmap=temp,
						pos=(posx, offset - 9)
					),
					flag=wx.BOTTOM | wx.ALIGN_BOTTOM,
					proportion=1
				)
				posx += (count + 10)
				self.spbox.Add(tsizer)
		self.sp.SetSizer(self.spbox)

	def initUI(self):
		self.SetBackgroundColour(
			self.config.loadedConfig["colorBg"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		vbox = wx.BoxSizer(wx.VERTICAL)

		title = wx.StaticText(self, label=_(" Athlete picture"))
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
		vbox.Add(self.spbox)

		self.sp = scrolled.ScrolledPanel(
			self,
			name=_("out"),
			size=self.GetSize(),
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)

		self.sp.SetSizer(self.spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp, flag=wx.ALL)

		# dynamic image layout
		self.Bind(wx.EVT_TIMER, self.onTimer)

		self.SetSizer(vbox)
		self.Show()
