from ctypes import *
import random
import numpy as np

import math
from config.yoloConfig import number, number20
# AART_project/src/config
# 導入各自機器的檔案路徑

def sample(probs):
	s = sum(probs)
	probs = [a / s for a in probs]
	r = random.uniform(0, 1)
	for i in range(len(probs)):
		r = r - probs[i]
		if r <= 0:
			return i
	return len(probs) - 1


def c_array(ctype, values):
	arr = (ctype * len(values))()
	arr[:] = values
	return arr


class BOX(Structure):
	_fields_ = [
		("x", c_float),
		("y", c_float),
		("w", c_float),
		("h", c_float)
	]


class DETECTION(Structure):
	_fields_ = [
		("bbox", BOX),
		("classes", c_int),
		("prob", POINTER(c_float)),
		("mask", POINTER(c_float)),
		("objectness", c_float),
		("sort_class", c_int)
	]


class IMAGE(Structure):
	_fields_ = [
		("w", c_int),
		("h", c_int),
		("c", c_int),
		("data", POINTER(c_float))
	]


class METADATA(Structure):
	_fields_ = [
		("classes", c_int),
		("names", POINTER(c_char_p))
	]

darknet = number()
# darknet = number20()

darknet.config()
defaultModelFolder = darknet.defaultModelFolder
darknetCfg = darknet.darknetCfg
darnetWeights = darknet.darnetWeights
darknetData = darknet.darknetData

myHomeDir = darknet.darknetDir
lib = CDLL(myHomeDir + "libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [
	c_void_p, c_int, c_int,
	c_float, c_float, POINTER(c_int),
	c_int, POINTER(c_int)
]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)


def classify(net, meta, im):
	# check if image is an OpenCV frame
	'''
	if isinstance(im, np.ndarray):
		# GET C,H,W, and DATA values
		img = im.transpose(2, 0, 1)
		c, h, w = img.shape[0], img.shape[1], img.shape[2]
		nump_data = img.ravel() / 255.0
		nump_data = np.ascontiguousarray(nump_data, dtype=np.float32)

		# make c_type pointer to numpy array
		ptr_data = nump_data.ctypes.data_as(POINTER(c_float))

		# make IMAGE data type
		im = IMAGE(w=w, h=h, c=c, data=ptr_data)

	else:
		im = load_image(im, 0, 0)
	'''

	out = predict_image(net, im)
	res = []
	for i in range(meta.classes):
		res.append((meta.names[i], out[i]))
	res = sorted(res, key=lambda x: -x[1])
	return res


def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
	# check if image is an OpenCV frame
	'''
	if isinstance(image, np.ndarray):
		# GET C,H,W, and DATA values
		img = image.transpose(2, 0, 1)
		c, h, w = img.shape[0], img.shape[1], img.shape[2]
		nump_data = img.ravel() / 255.0
		nump_data = np.ascontiguousarray(nump_data, dtype=np.float32)

		# make c_type pointer to numpy array
		ptr_data = nump_data.ctypes.data_as(POINTER(c_float))

		# make IMAGE data type
		im = IMAGE(w=w, h=h, c=c, data=ptr_data)

	else:
		im = load_image(image, 0, 0)
	'''

	im, image = array_to_image(image)
	rgbgr_image(im)
	num = c_int(0)
	pnum = pointer(num)
	predict_image(net, im)
	dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
	num = pnum[0]
	if (nms):
		do_nms_obj(dets, num, meta.classes, nms)

	res = []
	for j in range(num):
		for i in range(meta.classes):
			if dets[j].prob[i] > 0:
				b = dets[j].bbox
				res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
	res = sorted(res, key=lambda x: -x[1])

	if isinstance(image, bytes):
		free_image(im)
	free_detections(dets, num)
	return res


def array_to_image(arr):
	# need to return old values to avoid python freeing memory
	arr = arr.transpose(2, 0, 1)
	c, h, w = arr.shape[0:3]
	arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
	data = arr.ctypes.data_as(POINTER(c_float))
	im = IMAGE(w, h, c, data)
	return im, arr


if __name__ == "__main__":
	net = load_net(b"./yolov3.cfg", b"./yolov3.weights", 0)
	meta = load_meta(b"./coco.data")
	r = detect(net, meta, "dog.jpg")
