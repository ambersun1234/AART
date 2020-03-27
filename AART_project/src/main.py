import wx
import wx.media
import os
import sys

from device.device import SelectDeviceDialog
from input.input import InputPanel
from media.media import MediaPanel
from output.output import OutputTextPanel, OutputPicPanel
from welcome.welcome import WelcomeGuide
from config.systemConfig import systemConfig
from neuralNetwork.prediction import runNeuralNetwork

import gc

import gettext

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# show error only

class Frame(wx.Frame):
	def __init__(self, parent):
		super(Frame, self).__init__(parent)
		self.currentScreenX = 0
		self.currentScreenY = 0
		self.initSize()
		self.rootPath = os.path.abspath(__file__)

		self.config = systemConfig(self.rootPath)
		self.nn = runNeuralNetwork()

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

		self.OutputPicPanel = OutputPicPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.3
			),
			config=self.config,
			nn=self.nn
		)

		self.inputPanel = InputPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.3
			),
			config=self.config,
			nn=self.nn
		)
		self.OutputTextPanel = OutputTextPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.7
			),
			config=self.config,
			nn=self.nn
		)

		self.mediaPanel = MediaPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.7
			),
			config=self.config,
			path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
			nn=self.nn,
			ot=self.OutputTextPanel,
			op=self.OutputPicPanel
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
		hboxUp.Add(line)
		hboxUp.Add(self.OutputTextPanel)

		hboxBottom.Add(self.OutputPicPanel)
		line = wx.StaticLine(self, size=(5, 5), style=wx.LI_VERTICAL)
		hboxBottom.Add(line)
		hboxBottom.Add(self.inputPanel)

		vbox.Add(hboxUp)
		line = wx.StaticLine(self, size=(5, 5), style=wx.LI_VERTICAL)
		line.SetBackgroundColour("#f75b25")
		vbox.Add(line)
		vbox.Add(hboxBottom)

		self.SetSizer(vbox)
		self.Show()

		with self.welcome as dlg:
			dlg.ShowModal()
			if not self.welcome.path == "":
				dlg.Destroy()
				self.mediaPanel.doLoad(self.welcome.path)
				dlg.Destroy()
			else:
				dlg.Destroy()

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
		# self.currentScreenX = screenX * 0.75
		# self.currentScreenY = screenY * 0.8

		self.currentScreenX = screenX
		self.currentScreenY = screenY

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
			if not self.config.loadedConfig["language"] == "tw" else "  "

		op = wx.Menu()
		op.Append(11, _("&Select camera\tCtrl+c"), _("Select camera"))
		op.Append(14, _("&Select Video"), _("Select video"))
		op2 = wx.Menu()
		op2.Append(12, checkTw + _("&Traditional Chinese"), _("Traditional Chinese"))
		op2.Append(13, checkEn + _("&English"), _("English"))
		fileMenu.Append(wx.ID_ANY, _("&Open"), op)
		fileMenu.Append(21, _("&Choose language"), op2)
		fileMenu.Append(33, _("&Quit"), _("Quit application"))

		menuBar.Append(fileMenu, _("&File"))
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.onQuit, id=33)
		self.Bind(wx.EVT_MENU, self.onOpenVideo, id=14)
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
		if not lang == self.config.loadedConfig["language"]:
			self.config.storeLang(lang)
			self.config.save()
			self.onRestart(event)

	def onRestart(self, event):
		# restart program
		gc.collect()
		sys.stdout.flush()
		# sys.executable: find current python interpreter
		os.execl(
			os.path.abspath(sys.executable),
			"python",
			__file__,
			*sys.argv[1:]
		)

	def onSelectCamera(self, event):
		dialog = SelectDeviceDialog(
			None,
			title=_("Select web camera"),
			config=self.config
		)
		dialog.ShowModal()
		self.mediaPanel.doSelect(int(dialog.deviceID))
		self.inputPanel.inputReinit()
		self.nn.resetVar()
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
				self.nn.resetVar()
				self.mediaPanel.doLoad(path)
				self.inputPanel.inputReinit()
				self.config.storePath(path)
				self.config.save()

		dialog.Destroy()
		os.chdir(defaultPath)

	def onQuit(self, event):
		self.Close()

if __name__ == '__main__':
	# prevent program automatically
	# change current working directory by itself
	global defaultPath
	defaultPath = os.getcwd()

	app = wx.App(False)
	frame = Frame(None)
	app.MainLoop()
