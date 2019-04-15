import wx
import wx.media
import sys
import os

from src.device.device import SelectDeviceDialog
from src.input.input import InputPanel
from src.media.media import MediaPanel
from src.output.output import OutputTextPanel, OutputPicPanel
from src.welcome.welcome import WelcomeGuide
from src.config.configJSON import Config

import gettext

class Frame(wx.Frame):
	def __init__(self, parent):
		super(Frame, self).__init__(parent)
		self.currentScreenX = 0
		self.currentScreenY = 0
		self.initSize()

		self.config = Config(os.path.abspath(__file__))

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

		# set title
		self.SetTitle(title=_("Athlete Analysis of Real Time Sports Events( AART )"))

		self.mediaPanel = MediaPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.7
			),
			config=self.config
		)
		self.OutputPicPanel = OutputPicPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.3
			),
			config=self.config
		)

		self.inputPanel = InputPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.3
			),
			config=self.config
		)
		self.OutputTextPanel = OutputTextPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.7
			),
			config=self.config
		)

		self.welcome = WelcomeGuide(
			self,
			title=_("Welcome to AART"),
			size=(self.currentScreenX * 0.5, self.currentScreenY * 0.5),
			path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
			config=self.config
		)

		self.initUI()

	def initUI(self):
		self.initMenuBar()

		vbox = wx.BoxSizer(wx.VERTICAL)
		hboxUp = wx.BoxSizer(wx.HORIZONTAL)
		hboxBottom = wx.BoxSizer(wx.HORIZONTAL)

		hboxUp.Add(self.mediaPanel)
		line = wx.StaticLine(self, size=(5, 5), style=wx.LI_VERTICAL)
		line.SetForegroundColour("#f75b25")
		hboxUp.Add(line)
		hboxUp.Add(self.OutputTextPanel)

		hboxBottom.Add(self.OutputPicPanel)
		line = wx.StaticLine(self, size=(5, 5), style=wx.LI_VERTICAL)
		line.SetBackgroundColour("#f75b25")
		hboxBottom.Add(line)
		hboxBottom.Add(self.inputPanel)

		vbox.Add(hboxUp)
		line = wx.StaticLine(self, size=(5, 5), style=wx.LI_VERTICAL)
		line.SetBackgroundColour("#f75b25")
		vbox.Add(line)
		vbox.Add(hboxBottom)

		self.SetSizer(vbox)
		self.Show()

		self.welcome.ShowModal()
		if not self.welcome.path == "":
			self.mediaPanel.doLoad(self.welcome.path)
		self.welcome.Destroy()

	def getMinResolution(self):
		rx = 7680
		ry = 4320
		# get all displays
		displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
		for display in displays:
			tx, ty = display.GetGeometry().GetSize()
			rx = tx if tx < rx else rx
			ry = ty if ty < ry else ry
		return rx, ry

	def initSize(self):
		screenX, screenY = self.getMinResolution()
		self.currentScreenX = screenX * 0.75
		self.currentScreenY = screenY * 0.8

		# self.currentScreenX = screenX
		# self.currentScreenY = screenY

		self.SetSize(self.currentScreenX, self.currentScreenY)
		self.Centre()

	def initMenuBar(self):
		menuBar = wx.MenuBar()
		menuBar.SetFont(wx.Font(
			13,
			wx.FONTFAMILY_DEFAULT,
			wx.FONTSTYLE_NORMAL,
			wx.FONTWEIGHT_NORMAL)
		)
		fileMenu = wx.Menu()

		checkTw = "\u2714  " \
			if self.config.loadedConfig["language"] == "tw" else "  "
		checkEn = "\u2714  " \
			if self.config.loadedConfig["language"] != "tw" else "  "

		op = wx.Menu()
		op.Append(11, _("&Select camera\tCtrl+c"), _("Select camera"))
		op.Append(wx.ID_OPEN, _("&Select Video"), _("Select video"))
		op2 = wx.Menu()
		op2.Append(12, checkTw + _("&Traditional Chinese"), _("Traditional Chinese"))
		op2.Append(13, checkEn + _("&English"), _("English"))
		fileMenu.Append(wx.ID_ANY, _("&Open"), op)
		fileMenu.Append(21, _("&Choose language"), op2)
		fileMenu.Append(wx.ID_EXIT, _("&Quit"), _("Quit application"))

		menuBar.Append(fileMenu, _("&File"))
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.onOpenVideo, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.onSelectCamera, id=11)

		# set language
		self.Bind(
			wx.EVT_MENU,
			lambda event,
			lang="tw": self.onChangeLane(event, lang),
			id=12
		)  # traditional chinese
		self.Bind(
			wx.EVT_MENU,
			lambda event,
			lang="en": self.onChangeLane(event, lang),
			id=13
		)  # english

	def onChangeLane(self, event, lang):
		self.config.storeLang(lang)
		self.config.save()
		self.onRestart(event)

	def onRestart(self, event):
		# restart program
		os.execl(sys.executable, "python", __file__, *sys.argv[1:])

	def onSelectCamera(self, event):
		dialog = SelectDeviceDialog(
			None,
			title=_("Select web camera"),
			config=self.config
		)
		dialog.ShowModal()
		self.mediaPanel.doSelect(int(dialog.deviceID))
		dialog.Destroy()

	def onOpenVideo(self, event):
		dialog = wx.FileDialog(
			self,
			message=_("Choose a file"),
			wildcard=_("Video files(*.mp4;*.avi)|*.mp4;*.avi"),
			defaultFile="",
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR
		)
		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPaths()
			for path in paths:
				self.mediaPanel.doLoad(path)
				self.config.storePath(path)
				self.config.save()

		dialog.Destroy()

	def onQuit(self, event):
		self.Close()

if __name__ == '__main__':
	app = wx.App()
	frame = Frame(None)
	app.MainLoop()
