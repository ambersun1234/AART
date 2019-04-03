import wx
import wx.media
import cv2

class previewCamera(wx.Panel):
	def __init__(self, parent, deviceID):
		wx.Panel.__init__(self, parent)

		self.deviceIDT = deviceID
		self.deviceID = deviceID
		self.fps = 30
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

class MediaPanel(wx.Panel):
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent, size=size)

		self.type = {"webcam": 0, "video": 1}
		self.choice = self.type["webcam"]
		self.captureID = -1
		self.cap = None
		self.videoPath = ""

		# get current panel size
		self.currentWidth, self.currentHeight = size
		self.currentHeight = (int)(self.currentHeight)
		self.currentWidth = (int)(self.currentWidth)

		self.fps = 30
		self.timer = wx.Timer(self)

		self.bmp = None

		self.initUI()

	def initUI(self):
		self.SetBackgroundColour("gray")
		self.Show()

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

			# start stream
			self.timer.Start(1000. / self.fps)

	def doLoad(self, path):
		self.videoPath = path
		self.choice = self.type["video"]
		self.iterate()

	def doSelect(self, id):
		if not id == -1:
			self.captureID = id
			self.choice = self.type["webcam"]
			self.iterate()
