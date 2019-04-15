import wx
import wx.media
import cv2

import gettext

class PreviewCamera(wx.Panel):
	def __init__(self, parent, deviceID):
		wx.Panel.__init__(self, parent)

		self.deviceIDT = deviceID
		self.deviceID = deviceID
		self.fps = 20
		self.timer = wx.Timer(self)
		self.timer.Start(1000. / self.fps)

		self.capture = cv2.VideoCapture(self.deviceID)
		ret, self.defaultFrame = self.capture.read()

		self.defaultFrame = cv2.cvtColor(self.defaultFrame, cv2.COLOR_BGR2RGB)

		self.bmp = wx.Bitmap.FromBuffer(
			self.capture.get(cv2.CAP_PROP_FRAME_WIDTH),
			self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
			self.defaultFrame
		)

		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_TIMER, self.getNext)

		self.Show()

	def onChangeCapture(self):
		if self.deviceIDT != self.deviceID:
			self.deviceID = self.deviceIDT
			self.capture = cv2.VideoCapture(self.deviceID)

	def onPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0)

	def getNext(self, event):
		self.onChangeCapture()
		ret, frame = self.capture.read()

		if ret:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			self.bmp.CopyFromBuffer(frame)
			self.Refresh()

class MediaFrame(wx.Panel):
	def __init__(self, parent, size, config):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.mediaBar = None
		self.bmp = None
		self.choice = None
		self.config = config
		self.control = True
		self.captureID = -1
		self.cap = None
		self.videoPath = ""
		self.type = {"webcam": 0, "video": 1}

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

		# set playing speed
		self.fps = 30
		self.timer = wx.Timer(self)

		# get current size
		self.currentWidth, self.currentHeight = size
		self.currentHeight = int(self.currentHeight)
		self.currentWidth = int(self.currentWidth)

		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

	def onPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0)

	def getNext(self, event):
		# binding mediaBar slider event
		if self.choice == self.type["video"]:
			self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.mediaBar.slider.GetValue())

		if self.choice == self.type["video"] and \
			self.mediaBar.slider.GetValue() == self.mediaBar.slider.GetMax():
			self.timer.Stop()
			self.mediaBar.controlButton.SetLabel(_("Play"))
			# which means the video play to the end and stop

		ret, frame = self.cap.read()

		if ret:
			# resize to fix current window size
			frame = cv2.resize(
				frame,
				(self.currentWidth, self.currentHeight),
				interpolation=cv2.INTER_CUBIC
			)
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			self.bmp.CopyFromBuffer(frame)

			# refresh mediaBar slider
			if self.choice == self.type["video"]:
				self.mediaBar.onTimer()

			self.Refresh()

	def iterate(self):
		self.cap = cv2.VideoCapture(
			self.captureID if self.choice == 0
			else self.videoPath
		)

		# check capture opened successfully
		# opencv will force to stop the application cause MessageBox is not woking
		if self.cap is None or not self.cap.isOpened():
			if self.type == 0:
				temp = _("Unable to load webcam, it might be busy.\n")
				_("Try it again")
			else:
				temp = _("Loading file failed, please check again")

			wx.MessageBox(
				temp,
				_("ERROR"),
				wx.ICON_ERROR | wx.OK
			)
		else:
			if self.choice == self.type["video"]:
				# set mediaBar slider max value
				self.mediaBar.slider.SetMax(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
			else:
				self.mediaBar.slider.SetMin(0)
				self.mediaBar.slider.SetMax(0)
				self.mediaBar.slider.SetValue(1)

			# read first image from current selected capture
			ret, frame = self.cap.read()

			# resize to fix current window size
			self.bmp = cv2.resize(
				frame,
				(self.currentWidth, self.currentHeight),
				interpolation=cv2.INTER_CUBIC
			)

			self.bmp = cv2.cvtColor(self.bmp, cv2.COLOR_BGR2RGB)

			self.bmp = wx.Bitmap.FromBuffer(
				self.currentWidth,
				self.currentHeight,
				self.bmp
			)

			# need to bind event here
			# because wx.EVT_PAINT will execute immediately when bind success
			self.Bind(wx.EVT_PAINT, self.onPaint)
			self.Bind(wx.EVT_TIMER, self.getNext)
			self.Bind(wx.EVT_CHAR, self.onKey)

			self.timer.Start(1000. / self.fps)

	def onKey(self, event):
		keycode = event.GetKeyCode()

		# play pause setup
		if keycode == wx.WXK_SPACE or chr(keycode) == "k" or chr(keycode) == "K":
			# pause or play check based on self.control
			if self.choice == self.type["video"] and \
				self.mediaBar.controlButton.GetLabel() == _("Play") and \
				self.mediaBar.slider.GetValue() == self.mediaBar.slider.GetMax():
				self.mediaBar.slider.SetValue(0)
				self.timer.Start(1000. / self.fps)
				self.control = True
				self.mediaBar.controlButton.SetLabel(_("Pause"))
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
			else:
				if self.control:
					self.timer.Stop()
					self.mediaBar.controlButton.SetLabel(_("Play"))
				else:
					self.timer.Start(1000. / self.fps)
					self.mediaBar.controlButton.SetLabel(_("Pause"))
				self.control = not self.control

		if self.choice == self.type["video"]:
			if chr(keycode) == "j" or chr(keycode) == "J":
				self.mediaBar.slider.SetValue(
					self.mediaBar.slider.GetValue() - self.fps * 10
				)
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.mediaBar.slider.GetValue())

			elif chr(keycode) == "l" or chr(keycode) == "L":
				self.mediaBar.slider.SetValue(
					self.mediaBar.slider.GetValue() + self.fps * 10
				)
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.mediaBar.slider.GetValue())

			elif keycode == wx.WXK_LEFT:
				self.mediaBar.slider.SetValue(
					self.mediaBar.slider.GetValue() - self.fps * 5
				)
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.mediaBar.slider.GetValue())

			elif keycode == wx.WXK_RIGHT:
				self.mediaBar.slider.SetValue(
					self.mediaBar.slider.GetValue() + self.fps * 5
				)
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.mediaBar.slider.GetValue())

	def reinit(self):
		self.fps = 30
		self.videoPath = ""
		self.cap = None
		self.captureID = -1
		self.control = True
		self.choice = None
		self.bmp = None

		self.mediaBar.slider.SetMin(0)
		self.mediaBar.slider.SetValue(0)
		self.mediaBar.controlButton.SetLabel(_("Pause"))
		# reinitialize mediaFrame self variable
		# since user may change webcam or video during broadcast

	def load(self, path, choice):
		self.reinit()
		self.mediaBar.enableBtn()

		self.videoPath = path
		self.choice = choice
		self.iterate()

	def select(self, capID, choice):
		if not capID == -1:
			self.reinit()
			self.mediaBar.disableBtn()

			self.captureID = capID
			self.choice = choice
			self.iterate()

class MediaBar(wx.Panel):
	def __init__(self, parent, size, config, mediaFrame):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.mediaFrame = mediaFrame
		self.mediaLength = 0
		self.width, self.height = self.GetSize()
		self.slider = None

		self.controlButton = None
		self.forward = None
		self.backward = None

		self.initUI()

	def onChange(self, event):
		track = self.slider.GetValue()
		self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, track)
		self.mediaFrame.SetFocus()

	def initUI(self):
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)
		self.controlButton = wx.Button(self, label=_("Pause"))
		self.forward = wx.Button(self, label=_("forward"))
		self.backward = wx.Button(self, label=_("backward"))
		self.slider = wx.Slider(
			self,
			minValue=0,
			maxValue=0,  # set max value in mediaFrame when video is loaded
			style=wx.SL_HORIZONTAL,
			size=(self.width * 0.75, self.height)
		)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.slider, flag=wx.ALIGN_LEFT | wx.ALL)
		hbox.AddSpacer(5)
		hbox.Add(self.backward, flag=wx.ALIGN_RIGHT | wx.ALL)
		hbox.AddSpacer(3)
		hbox.Add(self.controlButton, flag=wx.ALL | wx.ALIGN_RIGHT)
		hbox.AddSpacer(3)
		hbox.Add(self.forward, flag=wx.ALIGN_RIGHT | wx.ALL)
		self.SetSizer(hbox)

		# key event binding
		self.forward.Bind(wx.EVT_BUTTON, self.onForward)
		self.backward.Bind(wx.EVT_BUTTON, self.onBackward)
		# forward & backword in button --> move 150 frame
		self.controlButton.Bind(wx.EVT_BUTTON, self.onKeyBtn)

		self.slider.Bind(
			wx.EVT_SLIDER,
			self.onChange
		)

	def onTimer(self):
		self.slider.SetValue(self.slider.GetValue() + 1)

	def disableBtn(self):
		self.forward.Disable()
		self.backward.Disable()

	def enableBtn(self):
		self.forward.Enable()
		self.backward.Enable()

	# key event button
	def onForward(self, event):
		if self.mediaFrame.choice == self.mediaFrame.type["video"]:
			self.slider.SetValue(self.slider.GetValue() + self.mediaFrame.fps * 5)
			self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, self.slider.GetValue())

	def onBackward(self, event):
		if self.mediaFrame.choice == self.mediaFrame.type["video"]:
			self.slider.SetValue(self.slider.GetValue() - self.mediaFrame.fps * 5)
			self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, self.slider.GetValue())

	def onKeyBtn(self, event):
		if self.mediaFrame.choice == self.mediaFrame.type["video"] and \
			self.controlButton.GetLabel() == _("Play") and \
			self.slider.GetValue() == self.slider.GetMax():
			self.slider.SetValue(0)
			self.mediaFrame.timer.Start(1000. / self.mediaFrame.fps)
			# self.mediaFrame.control = True
			self.controlButton.SetLabel(_("Pause"))
			self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
			self.mediaFrame.control = not self.mediaFrame.control

		else:
			# pause or play check based on self.control
			if self.mediaFrame.control:
				self.mediaFrame.timer.Stop()
				self.controlButton.SetLabel(_("Play"))
			else:
				self.mediaFrame.timer.Start(1000. / self.mediaFrame.fps)
				self.controlButton.SetLabel(_("Pause"))
			self.mediaFrame.control = not self.mediaFrame.control

class MediaPanel(wx.Panel):
	def __init__(self, parent, size, config):
		# frame display size
		w, h = size
		frameSize = (w, h * 0.95)
		barSize = (w, h * 0.05)
		wx.Panel.__init__(self, parent, size=size)
		self.type = {"webcam": 0, "video": 1}

		self.mediaFrame = MediaFrame(
			self,
			size=frameSize,
			config=config
		)
		self.mediaBar = MediaBar(
			self,
			size=barSize,
			config=config,
			mediaFrame=self.mediaFrame
		)

		# Caution: use it carefully,
		# it will let mediaFrame have mediaBar instance
		self.mediaFrame.mediaBar = self.mediaBar

		# separate mediaFrame and mediaBar vertically
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.mediaFrame)
		vbox.Add(self.mediaBar)
		self.SetSizer(vbox)

		self.initUI()

	def initUI(self):
		self.Show()

	def doLoad(self, path):
		self.mediaFrame.load(path, self.type["video"])

	def doSelect(self, capID):
		if not capID == -1:
			self.mediaFrame.select(capID, self.type["webcam"])
