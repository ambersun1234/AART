import wx
import wx.media
import cv2

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
				temp = "Unable to load webcam, it might be busy.\n"
				"Try it again"
			else:
				temp = "Loading file failed, please check again"

			wx.MessageBox(
				temp,
				"ERROR",
				wx.ICON_ERROR | wx.OK
			)
		else:
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

			# key event binding
			self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

			self.timer.Start(1000. / self.fps)

	def onKey(self, event):
		keycode = event.GetKeyCode()

		# play pause setup
		if keycode == wx.WXK_SPACE:
			self.control = not self.control
			# pause or play check based on self.control
			if not self.control:
				self.timer.Stop()
				self.mediaBar.controlButton.SetLabel("Play")
			else:
				self.timer.Start(1000. / self.fps)
				self.mediaBar.controlButton.SetLabel("Pause")

	def load(self, path, choice):
		self.videoPath = path
		self.choice = choice
		self.iterate()

	def select(self, capID, choice):
		if not capID == -1:
			self.captureID = capID
			self.choice = choice
			self.iterate()

class MediaBar(wx.Panel):
	def __init__(self, parent, size, config, mediaFrame):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.mediaFrame = mediaFrame
		self.controlButton = None

		self.initUI()

	def initUI(self):
		self.SetBackgroundColour(
			"#4c4c4c" if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.controlButton = wx.Button(self, label="Pause")
		hbox.Add(self.controlButton)

		self.controlButton.Bind(wx.EVT_BUTTON, self.onKey)

	def onKey(self, event):
		self.mediaFrame.control = not self.mediaFrame.control
		# pause or play check based on self.control
		if not self.mediaFrame.control:
			self.mediaFrame.timer.Stop()
			self.controlButton.SetLabel("Play")
		else:
			self.mediaFrame.timer.Start(1000. / self.mediaFrame.fps)
			self.controlButton.SetLabel("Pause")

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
