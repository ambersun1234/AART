import wx
import wx.media
import os
import subprocess

class StaticText(wx.StaticText):
	"""
	A StaticText that only updates the label if it has changed, to
	help reduce potential flicker since these controls would be
	updated very frequently otherwise.
	"""
	def SetLabel(self, label):

		if label != self.GetLabel():
			wx.StaticText.SetLabel(self, label)

class Panel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)
		try:
			self.mc = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
		except NotImplementedError:
			self.Destroy()
			raise

		self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

		btn2 = wx.Button(self, -1, "Play")
		self.Bind(wx.EVT_BUTTON, self.OnPlay, btn2)
		self.playBtn = btn2

		btn3 = wx.Button(self, -1, "Pause")
		self.Bind(wx.EVT_BUTTON, self.OnPause, btn3)

		btn4 = wx.Button(self, -1, "Stop")
		self.Bind(wx.EVT_BUTTON, self.OnStop, btn4)

		slider = wx.Slider(self, -1, 0, 0, 0)
		self.slider=slider
		self.st_size=StaticText(self, -1, size=(100, -1))
		self.st_len= StaticText(self, -1, size=(100, -1))
		self.st_pos=StaticText(self, -1, size=(100, -1))

		sizer = wx.GridBagSizer(5, 5)
		sizer.Add(self.mc, (1, 1), span=(5, 1))#, flag=wx.EXPAND)
		sizer.Add(btn2, (2, 3))
		sizer.Add(btn3, (3, 3))
		sizer.Add(btn4, (4, 3))
		sizer.Add(slider, (6, 1), flag=wx.EXPAND)
		sizer.Add(self.st_size, (1, 5))
		sizer.Add(self.st_len,  (2, 5))
		sizer.Add(self.st_pos,  (3, 5))
		self.SetSizer(sizer)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.timer.Start(100)

	def DoLoadFile(self, path):
		self.playBtn.Disable()

		if not self.mc.Load(path):
			wx.MessageBox("Unable to load %s: Unsupported format?" % path,
						  "ERROR",
						  wx.ICON_ERROR | wx.OK)
		else:
			self.mc.SetInitialSize()
			self.GetSizer().Layout()
			self.slider.SetRange(0, self.mc.Length())


	def OnMediaLoaded(self, evt):
		self.playBtn.Enable()


	def OnPlay(self, evt):
		if not self.mc.Play():
			wx.MessageBox("Unable to Play media : Unsupported format?",
						  "ERROR",
						  wx.ICON_ERROR | wx.OK)
		else:
			self.mc.SetInitialSize()
			self.GetSizer().Layout()
			self.slider.SetRange(0, self.mc.Length())

	def OnPause(self, evt):
		self.mc.Pause()


	def OnStop(self, evt):
		self.mc.Stop()

	def OnSeek(self, evt):
		offset = self.slider.GetValue()
		self.mc.Seek(offset)

	def OnTimer(self, evt):
		offset = self.mc.Tell()
		self.slider.SetValue(offset)
		self.st_size.SetLabel('size: %s' % self.mc.GetBestSize())
		self.st_len.SetLabel('length: %d seconds' % (self.mc.Length()/1000))
		self.st_pos.SetLabel('position: %d' % offset)


	def ShutdownDemo(self):
		self.timer.Stop()
		del self.timer

class PopupWindow(wx.PopupWindow):
	def __init__(self, parent):
		wx.PopupWindow.__init__(self, parent)
		panel = wx.Panel(self)
		self.panel = panel
		panel.SetBackgroundColour("CADET BLUE")

		st = wx.StaticText(panel, -1,
							"This is a special kind of top level\n"
							"window that can be used for\n"
							"popup menus, combobox popups\n"
							"and such.\n\n"
							"Try positioning the demo near\n"
							"the bottom of the screen and \n"
							"hit the button again.\n\n"
							"In this demo this window can\n"
							"be dragged with the left button\n"
							"and closed with the right."
							,
							pos=(10,10))
		sz = st.GetBestSize()
		self.SetSize( (sz.width+20, sz.height+20) )
		panel.SetSize( (sz.width+20, sz.height+20) )

		panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
		panel.Bind(wx.EVT_MOTION, self.OnMouseMotion)
		panel.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
		panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		st.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
		st.Bind(wx.EVT_MOTION, self.OnMouseMotion)
		st.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
		st.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

		wx.CallAfter(self.Refresh)

	def OnMouseLeftDown(self, evt):
		self.Refresh()
		self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
		self.wPos = self.ClientToScreen((0,0))
		self.panel.CaptureMouse()

	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
			nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
					self.wPos.y + (dPos.y - self.ldPos.y))
			self.Move(nPos)

	def OnMouseLeftUp(self, evt):
		if self.panel.HasCapture():
			self.panel.ReleaseMouse()

	def OnRightUp(self, evt):
		self.Show(False)
		self.Destroy()

class Frame(wx.Frame):
	def __init__(self, parent, title):
		super(Frame, self).__init__(parent, title=title)
		self.initUI()

	def initUI(self):
		self.initMenuBar()
		self.initSize()
		self.Show()

	def initSize(self):
		screenX, screenY=wx.GetDisplaySize()
		screenX = screenX * 0.75
		screenY = screenY * 0.8

		self.SetSize(screenX,screenY)
		self.Centre()

	def initMenuBar(self):
		menuBar = wx.MenuBar()
		fileMenu = wx.Menu()

		fileMenu.Append(wx.ID_NEW, "&New", "New file")
		op = wx.Menu()
		op.Append(11, "&Select camera\tCtrl+c", "Select camera")
		op.Append(wx.ID_OPEN, "&Select Video", "Select video")
		fileMenu.Append(wx.ID_ANY, "&Open", op)
		fileMenu.Append(wx.ID_SAVE, "&Save", "Save file")
		fileMenu.Append(wx.ID_SAVEAS, "&Save as", "Save file as")
		fileMenu.Append(wx.ID_EXIT, "&Quit", "Quit application")

		menuBar.Append(fileMenu, "&File")
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.onOpen, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.onSelect, id=11)

	def onSelect(self, event):
		# fetch video id
		p = subprocess.Popen("./fetch.sh", shell=True, executable='/bin/bash', stdout=subprocess.PIPE)
		for element in p.stdout.readlines():
			print( element )
		temp = PopupWindow(self.GetTopLevelParent())
		temp.Show()

	def onOpen(self, event):
		dialog = wx.FileDialog(self, message="Choose a file", wildcard="*.mp4", defaultFile="", style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)
		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPaths()
			for path in paths:
				Panel.DoLoadFile(panel, path)
		dialog.Destroy()

	def OnQuit(self, event):
		self.Close()

if __name__ == '__main__':
	app = wx.App()
	frame = Frame(None, title="Athlete Analysis of Real Time Sports Events( AART )")
	panel = Panel(frame)
	app.MainLoop()