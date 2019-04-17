import wx
import wx.lib.scrolledpanel as scrolled

import gettext

class OutputTextPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)

		self.text = {
			"1": "dribbling",
			"2": "layup",
			"3": "shooting",
			"4": "dribbling",
			"5": "layup",
			"6": "dribbling",
			"7": "dribbling",
			"8": "layup",
			"9": "dribbling",
			"10": "dribbling",
			"11": "dribbling",
			"12": "dribbling",
			"13": "dribbling",
			"14": "layup",
			"15": "dribbling",
			"16": "layup",
			"17": "dribbling",
			"18": "layup",
			"19": "dribbling",
			"20": "dribbling",
			"21": "shooting",
			"22": "dribbling",
			"23": "shooting",
			"24": "dribbling",
			"25": "shooting",
			"26": "dribbling"
		}
		self.config = config
		self.sp = None

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
		spbox = wx.BoxSizer(wx.VERTICAL)

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
		vbox.Add(title, flag=wx.ALL | wx.EXPAND)
		vbox.Add(
			wx.StaticLine(
				self,
				style=wx.LI_HORIZONTAL
			),
			flag=wx.ALL | wx.EXPAND
		)
		vbox.AddSpacer(5)

		check = False
		for key, value in self.text.items():
			temp = wx.StaticText(
				self.sp,
				label="   {} {}: {}".format(_("Athlete"), _(key), _(value)),
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
				spbox.AddSpacer(5)
			else:
				check = True
			spbox.Add(temp, flag=wx.EXPAND | wx.ALL)

		self.sp.SetSizer(spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp, flag=wx.ALL)

		self.SetSizer(vbox)
		self.Show()

class OutputPicPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.sp = None

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
		spbox = wx.BoxSizer(wx.HORIZONTAL)

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
		vbox.Add(spbox)

		self.sp.SetSizer(spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp, flag=wx.ALL)

		self.SetSizer(vbox)
		self.Show()
