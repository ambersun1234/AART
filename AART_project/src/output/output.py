import wx
import wx.lib.scrolledpanel as scrolled
from PIL import Image
import math
import cv2
import collections
import re

import gettext

def atoi(text):
	return int(text) if text.isdigit() else text

	# natural sorting
def nsort(text):
	return [atoi(c) for c in re.split(r'(\d+)', text)]

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
		self.fps = 10
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
			od = {
				k: v for k, v in sorted(
					self.nn._odict.items(),
					key=lambda x: nsort(x[0])
				)
			}
			self.spbox.Clear(True)
			check = True
			for number, posture in od.items():
				# up and down space
				if not check:
					self.spbox.AddSpacer(10)
				else:
					self.spbox.AddSpacer(5)

				hbox = wx.BoxSizer(wx.HORIZONTAL)

				# text first part
				text = wx.StaticText(
					self.sp,
					label=" {} {}: ".format(_("Athlete"), number)
				)
				text.SetForegroundColour(self.config.loadedConfig["colorText"])
				text.SetBackgroundColour("black")
				text.SetFont(
					wx.Font(
						self.config.loadedConfig["fontSize"],
						family=wx.DEFAULT,
						style=wx.NORMAL,
						weight=wx.NORMAL
					)
				)

				# text second part
				text2 = wx.StaticText(
					self.sp,
					label="{}".format(_(posture))
				)
				text2.SetForegroundColour(self.config.loadedConfig["colorText"])
				text2.SetFont(
					wx.Font(
						self.config.loadedConfig["fontSize"],
						family=wx.DEFAULT,
						style=wx.NORMAL,
						weight=wx.NORMAL
					)
				)

				# hbox part
				hbox.AddSpacer(20)
				hbox.Add(text)
				hbox.AddSpacer(5)
				hbox.Add(text2)

				self.spbox.Add(hbox)

		self.sp.SetSizer(self.spbox)
		self.sp.SetupScrolling()

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

		self.sp.SetSizer(self.spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp)

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
		self.tw = math.floor(self.w * 0.14)
		self.uh = math.floor(self.h * 0.1)
		self.dh = math.floor(self.h * 0.65)


		# dynamically get image from LSTM
		self.fps = 10
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
			od = {
				k: v for k, v in sorted(
					self.nn._oimg.items(),
					key=lambda x: nsort(x[0])
				)
			}
			self.spbox.Clear(True)
			posx = 0
			for number, img in od.items():
				tsizer = wx.BoxSizer(wx.VERTICAL)

				# make bmp
				img = cv2.resize(
					img,
					(self.tw, self.dh),
					interpolation=cv2.INTER_CUBIC
				)
				# cv2.imshow(number, img)
				img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
				img = Image.fromarray(img, "RGB")
				w, h = img.size
				temp = wx.Bitmap.FromBuffer(w, h, img.tobytes())

				# make text
				text = wx.StaticText(
					self.sp,
					label="  {}: {}".format(_("Athlete"), number),
					pos=(posx, 0)
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
				text.Center()
				tbmp = wx.StaticBitmap(
					self.sp,
					bitmap=temp,
					pos=(posx, self.uh + 2)
				)

				# set min width
				if text.GetSize()[0] < 140:
					text.SetMinSize(wx.Size(self.tw, text.GetSize()[1] + 10))
				else:
					tbmp.SetMinSize(wx.Size(text.GetSize()[0], tbmp.GetSize()[1]))

				# make sizer
				tsizer.Add(
					text,
					flag=wx.CENTER | wx.ALIGN_CENTER
				)
				tsizer.AddSpacer(5)
				tsizer.Add(
					tbmp,
					flag=wx.BOTTOM | wx.ALIGN_BOTTOM,
					proportion=1
				)

				self.spbox.Add(tsizer)
				self.spbox.AddSpacer(10)
			# self.timer.Stop()
			# cv2.waitKey(0)
		self.sp.SetSizer(self.spbox)
		self.sp.SetupScrolling(scroll_y=False)

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
		self.sp.SetupScrolling(scroll_y=False)
		vbox.Add(self.sp, flag=wx.ALL)

		# dynamic image layout
		self.Bind(wx.EVT_TIMER, self.onTimer)

		self.SetSizer(vbox)
		self.Show()
