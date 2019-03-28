import wx
import wx.media

import cv2

from src.device.device import SelectDeviceDialog
from src.input.input import InputPanel
from src.media.media import MediaPanel
from src.output.output import outputTextPanel, outputPicPanel

class Frame(wx.Frame):
	def __init__(self, parent, title):
		super(Frame, self).__init__(parent, title=title)
		self.currentScreenX = 0
		self.currentScreenY = 0
		self.initSize()

		self.mediaPanel = MediaPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.7
			)
		)
		self.outputPicPanel = outputPicPanel(
			self,
			size=(
				self.currentScreenX * 0.7,
				self.currentScreenY * 0.3
			)
		)

		self.inputPanel = InputPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.3
			)
		)
		self.outputTextPanel = outputTextPanel(
			self,
			size=(
				self.currentScreenX * 0.3,
				self.currentScreenY * 0.7
			)
		)

		self.initUI()

	def initUI(self):
		self.initMenuBar()

		vbox = wx.BoxSizer(wx.VERTICAL)
		hboxUp = wx.BoxSizer(wx.HORIZONTAL)
		hboxBottom = wx.BoxSizer(wx.HORIZONTAL)

		hboxUp.Add(self.mediaPanel)
		hboxUp.AddSpacer(5)  # add 5px space
		hboxUp.Add(self.outputTextPanel)

		hboxBottom.Add(self.outputPicPanel)
		hboxBottom.AddSpacer(5)  # add 5px space
		hboxBottom.Add(self.inputPanel)

		vbox.Add(hboxUp)
		vbox.AddSpacer(5)
		vbox.Add(hboxBottom)

		self.SetSizer(vbox)
		self.Show()

	def initSize(self):
		screenX, screenY = wx.GetDisplaySize()
		self.currentScreenX = screenX * 0.75
		self.currentScreenY = screenY * 0.8

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

		op = wx.Menu()
		op.Append(11, "&Select camera\tCtrl+c", "Select camera")
		op.Append(wx.ID_OPEN, "&Select Video", "Select video")
		fileMenu.Append(wx.ID_ANY, "&Open", op)
		fileMenu.Append(wx.ID_EXIT, "&Quit", "Quit application")

		menuBar.Append(fileMenu, "&File")
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.onOpenVideo, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.onSelectCamera, id=11)

	def onSelectCamera(self, event):
		dialog = SelectDeviceDialog(None, title="Select web camera")
		dialog.ShowModal()
		dialog.Destroy()

	def onOpenVideo(self, event):
		dialog = wx.FileDialog(
			self,
			message="Choose a file",
			wildcard="*.mp4",
			defaultFile="",
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR
		)
		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPaths()
			for path in paths:
				MediaPanel.DoLoadFile(self.mediaPanel, path)
		dialog.Destroy()

	def OnQuit(self, event):
		self.Close()

if __name__ == '__main__':
	app = wx.App()
	frame = Frame(
		None,
		title="Athlete Analysis of Real Time Sports Events( AART )"
	)
	app.MainLoop()
