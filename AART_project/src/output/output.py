import wx
import wx.lib.scrolledpanel as scrolled

class OutputTextPanel(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)

		self.text = {
			"person1": "pitch",
			"person2": "layup",
			"person3": "dreaming",
			"person4": "dreaming",
			"person5": "dreaming",
			"person6": "dreaming",
			"person7": "dreaming",
			"person8": "dreaming",
			"person9": "dreaming",
			"person10": "dreaming",
			"person11": "dreaming",
			"person12": "dreaming",
			"person13": "dreaming",
			"person14": "dreaming",
			"person15": "dreaming",
			"person16": "dreaming",
			"person17": "dreaming",
			"person18": "dreaming",
			"person19": "dreaming",
			"person20": "dreaming",
			"person21": "dreaming",
			"person22": "dreaming",
			"person23": "dreaming",
			"person24": "dreaming",
			"person25": "dreaming",
			"person26": "lalaland"
		}
		self.config = config
		self.sp = None
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		self.sp = scrolled.ScrolledPanel(
			self,
			name="out",
			size=self.GetSize(),
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)

		vbox = wx.BoxSizer(wx.VERTICAL)
		spbox = wx.BoxSizer(wx.VERTICAL)

		title = wx.StaticText(self, label=" Athlete action: ")
		title.SetForegroundColour(
			"white" if self.config.loadedConfig["theme"] == "dark" else "black"
		)
		title.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"],
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		vbox.AddSpacer(5)
		vbox.Add(title)
		vbox.AddSpacer(5)
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
			temp = wx.StaticText(self.sp, label="   {}: {}".format(key, value))
			temp.SetForegroundColour(
				"white" if self.config.loadedConfig["theme"] == "dark" else "black"
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
			spbox.Add(temp)

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
		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		self.sp = scrolled.ScrolledPanel(
			self,
			name="out",
			size=self.GetSize(),
			style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER
		)

		vbox = wx.BoxSizer(wx.VERTICAL)
		spbox = wx.BoxSizer(wx.HORIZONTAL)

		title = wx.StaticText(self, label=" Athlete picture")
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
		vbox.Add(spbox)

		self.sp.SetSizer(spbox)
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling()
		vbox.Add(self.sp, flag=wx.ALL)

		self.SetSizer(vbox)
		self.Show()
