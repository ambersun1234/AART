import wx
import wx.media
import cv2

import math

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
	def __init__(self, parent, size, config, nn, ot, op):
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
		self.nn = nn

		# output panel
		self.ot = ot
		self.op = op

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
			self.config.loadedConfig["colorBg"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
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
			self.mediaBar.controlButton.SetBitmap(self.mediaBar.playImg)
			# which means the video play to the end and stop
			# video read done, replay
			self.mediaBar.controlButton.SetBitmap(self.mediaBar.pauseImg)
			self.nn.resetVar()
			self.contInit()

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

			# pass image to neural network
			self.nn._iimg = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
			if self.nn._imode is None:
				self.nn._imode = 0
				self.nn._idict = dict()

			self.nn.trackNum(
				self.nn._imode,
				self.nn._idict,
				self.nn._iimg
			)
			self.timer.Stop()
			self.timer.Start(1000. / self.fps)

			# refresh mediaBar slider
			if self.choice == self.type["video"]:
				self.mediaBar.onTimer()

			# refersh video time
			self.mediaBar.calculateVideoTime(type="start")
			self.mediaBar.dynamicVideoTime()
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

			# set fps to video's fps
			self.fps = self.cap.get(cv2.CAP_PROP_FPS)
			self.mediaBar.fps = self.fps
			self.mediaBar.mediaLength = \
				int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) \
				if self.type["video"] == self.choice else 0

			# set video time by calling mediaBar.calculateVideoTime()
			self.mediaBar.calculateVideoTime(type="end")
			self.mediaBar.resetVideoTime()

			self.timer.Start(1000. / self.fps)

	def onKey(self, event):
		keycode = event.GetKeyCode()

		# play pause setup
		if keycode == wx.WXK_SPACE or chr(keycode) == "k" or chr(keycode) == "K":

			# pause or play check based on self.control
			if self.choice == self.type["video"] and \
				not self.timer.IsRunning() and \
				self.mediaBar.slider.GetValue() == self.mediaBar.slider.GetMax():

				self.mediaBar.slider.SetValue(0)
				self.timer.Start(1000. / self.fps)
				self.control = True
				self.mediaBar.controlButton.SetBitmap(self.mediaBar.pauseImg)
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

				# play output text & output picture
				self.ot.timer.Start(1000. / self.ot.fps)
				self.op.timer.Start(1000. / self.op.fps)
			else:
				if self.control:
					self.timer.Stop()

					# pause output text & output picture
					self.ot.timer.Stop()
					self.op.timer.Stop()
					self.mediaBar.controlButton.SetBitmap(self.mediaBar.playImg)
				else:
					self.timer.Start(1000. / self.fps)

					# play output text & output picture
					self.ot.timer.Start(1000. / self.ot.fps)
					self.op.timer.Start(1000. / self.op.fps)
					self.mediaBar.controlButton.SetBitmap(self.mediaBar.pauseImg)
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

	def contInit(self):
		# reinitialize mediaFrame self variable
		# this use in replay video only
		self.fps = 30
		self.cap = None
		self.bmp = None

		self.mediaBar.slider.SetMin(0)
		self.mediaBar.slider.SetValue(0)
		self.mediaBar.controlButton.SetBitmap(self.mediaBar.pauseImg)

		self.load(self.videoPath, self.choice)

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
		self.mediaBar.controlButton.SetBitmap(self.mediaBar.pauseImg)
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
	def __init__(self, parent, size, config, mediaFrame, path, ot, op):
		wx.Panel.__init__(self, parent, size=size)
		self.config = config
		self.mediaFrame = mediaFrame
		self.mediaLength = 0
		self.fps = 0
		self.width, self.height = self.GetSize()
		self.slider = None
		self.imgPath = path

		# output panel
		self.ot = ot
		self.op = op

		# video time bar
		self.startTime = {"h": 0, "m": 0, "s": 0}
		self.endTime = {"h": 0, "m": 0, "s": 0}

		# read img buttons
		self.playImg = wx.Image("{}/img/play.png".format(self.imgPath))
		self.pauseImg = wx.Image("{}/img/pause.png".format(self.imgPath))
		self.forwardImg = wx.Image("{}/img/forward.png".format(self.imgPath))
		self.backwardImg = wx.Image("{}/img/backward.png".format(self.imgPath))

		w, h = self.GetSize()
		# resize
		w = h - 10
		h = h - 20
		self.playImg = self.playImg.Scale(
			w,
			h,
			quality=wx.IMAGE_QUALITY_HIGH
		)
		self.pauseImg = self.pauseImg.Scale(
			w,
			h,
			quality=wx.IMAGE_QUALITY_HIGH
		)
		self.forwardImg = self.forwardImg.Scale(
			w,
			h,
			quality=wx.IMAGE_QUALITY_HIGH
		)
		self.backwardImg = self.backwardImg.Scale(
			w,
			h,
			quality=wx.IMAGE_QUALITY_HIGH
		)

		# convert img buttons to bmp
		self.playImg = self.playImg.ConvertToBitmap()
		self.pauseImg = self.pauseImg.ConvertToBitmap()
		self.forwardImg = self.forwardImg.ConvertToBitmap()
		self.backwardImg = self.backwardImg.ConvertToBitmap()

		self.controlButton = None
		self.forward = None
		self.backward = None

		self.stt = None
		self.ett = None

		self.initUI()

	def onChange(self, event):
		track = self.slider.GetValue()
		self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, track)
		self.mediaFrame.SetFocus()

	def initUI(self):
		self.SetBackgroundColour(
			self.config.loadedConfig["colorBg"]
			if self.config.loadedConfig["theme"] == "dark" else "white"
		)

		self.controlButton = wx.BitmapButton(self, bitmap=self.pauseImg)
		self.forward = wx.BitmapButton(self, bitmap=self.forwardImg)
		self.backward = wx.BitmapButton(self, bitmap=self.backwardImg)

		self.slider = wx.Slider(
			self,
			minValue=0,
			maxValue=0,  # set max value in mediaFrame when video is loaded
			style=wx.SL_HORIZONTAL,
			size=(self.width * 0.75, self.height)
		)

		self.stt = wx.StaticText(
			self,
			label="{:02d}:{:02d}:{:02d}".format(
				self.startTime["h"],
				self.startTime["m"],
				self.startTime["s"]
			)
		)
		self.ett = wx.StaticText(
			self,
			label="/{:02d}:{:02d}:{:02d}".format(
				self.endTime["h"],
				self.endTime["m"],
				self.endTime["s"]
			)
		)

		self.stt.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"] - 3,
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)
		self.ett.SetFont(wx.Font(
			self.config.loadedConfig["fontSize"] - 3,
			family=wx.DEFAULT,
			style=wx.NORMAL,
			weight=wx.NORMAL)
		)

		self.stt.SetForegroundColour(
			self.config.loadedConfig["colorText"]
		)
		self.ett.SetForegroundColour(
			self.config.loadedConfig["colorText"]
		)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		# slider
		hbox.Add(self.slider, flag=wx.ALIGN_LEFT | wx.ALL)
		hbox.AddSpacer(5)

		# video time
		hbox.Add(self.stt, flag=wx.ALIGN_CENTER)
		hbox.Add(self.ett, flag=wx.ALIGN_CENTER)
		hbox.AddSpacer(5)

		# buttons
		hbox.Add(self.backward, flag=wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_CENTER)
		hbox.AddSpacer(5)
		hbox.Add(self.controlButton, flag=wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER)
		hbox.AddSpacer(5)
		hbox.Add(self.forward, flag=wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_CENTER)
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

	def resetVideoTime(self):
		self.ett.SetLabel(
			"/{:02d}:{:02d}:{:02d}".format(
				self.endTime["h"],
				self.endTime["m"],
				self.endTime["s"]
			)
		)

	def dynamicVideoTime(self):
		self.stt.SetLabel(
			"{:02d}:{:02d}:{:02d}".format(
				self.startTime["h"],
				self.startTime["m"],
				self.startTime["s"]
			)
		)

	def calculateVideoTime(self, type="start"):
		if type == "start":
			totalSecond = math.floor(self.slider.GetValue() / self.fps)
		else:
			totalSecond = math.floor(self.mediaLength / self.fps)

		if totalSecond >= 3600:
			# over an hour
			hour = math.floor(totalSecond / 3600)
			minute = math.floor((totalSecond - hour * 3600) / 60)
			totalSecond = totalSecond - hour * 3600
			second = math.floor(totalSecond - minute * 60)

		elif totalSecond < 3600 and totalSecond >= 60:
			# between hour and second
			hour = 0
			minute = math.floor(totalSecond / 60)
			second = math.floor(totalSecond - minute * 60)
		else:
			hour = 0
			minute = 0
			second = math.floor(totalSecond)

		if type == "start":
			self.startTime["h"] = hour
			self.startTime["m"] = minute
			self.startTime["s"] = second
		else:
			if second < 0:
				second = 0
			self.endTime["h"] = hour
			self.endTime["m"] = minute
			self.endTime["s"] = second

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
		self.mediaFrame.SetFocus()

	def onBackward(self, event):
		if self.mediaFrame.choice == self.mediaFrame.type["video"]:
			self.slider.SetValue(self.slider.GetValue() - self.mediaFrame.fps * 5)
			self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, self.slider.GetValue())
		self.mediaFrame.SetFocus()

	def onKeyBtn(self, event):
		if self.mediaFrame.choice == self.mediaFrame.type["video"] and \
			not self.mediaFrame.timer.IsRunning() and \
			self.slider.GetValue() == self.slider.GetMax():
			self.slider.SetValue(0)
			self.mediaFrame.timer.Start(1000. / self.mediaFrame.fps)

			# play output text & output picture
			self.ot.timer.Start(1000. / self.ot.fps)
			self.op.timer.Start(1000. / self.op.fps)
			# self.mediaFrame.control = True
			self.controlButton.SetBitmap(self.pauseImg)
			self.mediaFrame.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
			self.mediaFrame.control = not self.mediaFrame.control

		else:
			# pause or play check based on self.control
			if self.mediaFrame.control:
				self.mediaFrame.timer.Stop()

				# play output text & output picture
				self.ot.timer.Stop()
				self.op.timer.Stop()

				# self.controlButton.SetLabel(_("Play"))
				self.controlButton.SetBitmap(self.playImg)
			else:
				self.mediaFrame.timer.Start(1000. / self.mediaFrame.fps)

				# play output text & output picture
				self.ot.timer.Start(1000. / self.ot.fps)
				self.op.timer.Start(1000. / self.op.fps)

				# self.controlButton.SetLabel(_("Pause"))
				self.controlButton.SetBitmap(self.pauseImg)
			self.mediaFrame.control = not self.mediaFrame.control
		self.mediaFrame.SetFocus()

class MediaPanel(wx.Panel):
	def __init__(self, parent, size, config, path, nn, ot, op):
		# frame display size
		w, h = size
		frameSize = (w, h * 0.95)
		barSize = (w, h * 0.05)
		wx.Panel.__init__(self, parent, size=size)
		self.type = {"webcam": 0, "video": 1}
		self.nn = nn
		self.ot = ot
		self.op = op

		self.mediaFrame = MediaFrame(
			self,
			size=frameSize,
			config=config,
			nn=self.nn,
			op=self.op,
			ot=self.ot
		)
		self.mediaBar = MediaBar(
			self,
			size=barSize,
			config=config,
			mediaFrame=self.mediaFrame,
			path=path,
			op=self.op,
			ot=self.ot
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
		self.outputReinit()

	def doSelect(self, capID):
		if not capID == -1:
			self.mediaFrame.select(capID, self.type["webcam"])
			self.outputReinit()

	def outputReinit(self):
		self.op.spbox.Clear(True)
		self.ot.spbox.Clear(True)
		self.op.sp.SetSizer(self.op.spbox)
		self.ot.sp.SetSizer(self.ot.spbox)
