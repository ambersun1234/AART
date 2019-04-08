import os
import errno
import sys
import cv2
import numpy as np
import math
import csv

from time import sleep

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

try:
    sys.path.append('/usr/local/python')
    from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` '
          'in CMake and have this Python script in the right folder?')
    raise e

# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "/home/louisme/library/openpose/models"
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
datum = op.Datum()

bodyPartName = [ "nose" , "neck" ,
				 "shoulderR" , "elbowR" , "handR" ,
				 "shoulderL" , "elbowL" , "handL" ,
				 "ass" ,
				 "legR" , "kneeR" , "feetR" ,
				 "legL" , "kneeL" , "feetL" ,
				 "eyeR" , "eyeL" , "earR" , "earL" ,
				 "footBoardR1" , "footBoardR2" , "footBoardR3" ,
				 "footBoardL1" , "footBoardL2" , "footBoardL3" ]
# 鼻子 , 頸部 1 , 2
# 右肩 , 右手軸 , 右手 3 , 4 , 5
# 左肩 , 左手軸 , 左手 6 , 7 , 8
# 屁股 9
# 右大腿 , 右膝蓋 , 右腳踝 10 , 11 , 12
# 左大腿 , 左膝蓋 , 左腳踝 13 , 14 , 15
# 右眼 左眼 右耳 左耳 16 , 17 , 18 , 19
# 左腳底板 20 , 21 , 22
# 右腳底板 23 , 24 , 25

storageKeypoints = np.zeros( ( 25 , 2 ) )
# initialize array with 0 in all 25 index

personFailed = []
keypointFailed = []
cropFailed = []
readFailed = []

personFailedCount = 0
keypointFailedCount = 0
cropFailedCount = 0
readFailedCount = 0

color = [ (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
		  (255, 0, 255), (0, 255, 255), (190, 190, 190), (190, 0, 0), (0, 190, 0),
		  (0, 0, 190), (190, 190, 0), (190, 0, 190), (0, 190, 190), (128, 128, 128),
		  (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128),
		  (0, 128, 128), (64, 64, 64), (64, 0, 0), (0, 64, 0), (0, 0, 64)]

# color = [ (0 , 0 , 255) , (0 , 0 , 255) , (0 , 255 , 255) , (0 , 255 , 255) , (0 , 255 , 255) ,
# 		  (0 , 255 , 0) , (0 , 255 , 0) , (0 , 255 , 0) , (0 , 0 , 255) , (255 , 178 , 178) ,
# 		  (255 , 178 , 178) , (255 , 178 , 178) , (255 , 0 , 0) , (255 , 0 , 0) , (255 , 0 , 0) ,
# 		  (139 , 26 , 85) , (139 , 26 , 85) , (139 , 26 , 85) , (139 , 26 , 85) , (255 , 0 , 0) ,
# 		  (255 , 0 , 0) , (255 , 0 , 0) , (255 , 178 , 178) , (255 , 178 , 178) , (255 , 178 , 178) ]
# BGR format
# 139 , 26 , 85   -> deep purple    5 face
# 0 , 0 , 255     -> deep red       3 body
# 0 , 255 , 255   -> yellow         2 right hand
# 0 , 255 , 0     -> light green    2 left hand
# 255 , 255 , 255 -> white          3 bud
# 255 , 178 , 178 -> light purple   5 right leg
# 255 , 0 , 0     -> deep blue      5 left leg

class Logger( object ):
	def __init__( self ):
		self.terminal = sys.stdout
		self.log = open( "./point.log" , "a" )

	def write( self , message ):
		self.terminal.write( message )
		self.log.write( message )

	def flush( self ):
		#this flush method is needed for python 3 compatibility.
		#this handles the flush command by doing nothing.
		#you might want to specify some extra behavior here.
		pass

def drawColor( normalizeImg , x , y , height , width , colorCount , thickness ):
	global color

	if thickness == 1:
		normalizeImg[ y    , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
	else:
		x1  = x + 1 if x + 1 < width  else width - 1
		x_1 = x - 1 if x - 1 >= 0     else 0
		x2  = x + 2 if x + 2 < width  else width - 1
		x_2 = x - 2 if x - 2 >= 0     else 0

		y1  = y + 1 if y + 1 < height else height - 1
		y_1 = y - 1 if y - 0 >= 0     else 0
		y2  = y + 2 if y + 2 < height else height - 1
		y_2 = y - 2 if y - 2 >= 0     else 0

		normalizeImg[ y    , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		normalizeImg[ y    , x1   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y    , x_1  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		normalizeImg[ y1   , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y1   , x1   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y1   , x_1  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		normalizeImg[ y_1  , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_1  , x1   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_1  , x_1  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		# right
		normalizeImg[ y2   , x2   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y1   , x2   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y    , x2   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_1  , x2   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_2  , x2   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		# up
		normalizeImg[ y2   , x1   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y2   , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y2   , x_1  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y2   , x_2  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		# left
		normalizeImg[ y1   , x_2  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y    , x_2  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_1  , x_2  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_2  , x_2  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

		# down
		normalizeImg[ y_2  , x_1  ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_2  , x    ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])
		normalizeImg[ y_2  , x1   ] = (color[ colorCount ][ 0 ] , color[ colorCount ][ 1 ] , color[ colorCount ][ 2 ])

def drawSumPicture( fileStoragePath , edge , part , x , y , outputHeight , outputWidth , index ):
	wholePart = cv2.imread( "{}/{}_{}_whole.jpg".format( fileStoragePath , edge , part ) )
	singlePart = cv2.imread( "{}/{}_{}_{}.jpg".format( fileStoragePath , edge , part , bodyPartName[ index ] ) )

	if wholePart is None:
		wholePart = np.ones( ( outputHeight , outputWidth , 3 ) , dtype = np.uint8 )
	if singlePart is None:
		singlePart = np.ones( ( outputHeight , outputWidth , 3 ) , dtype = np.uint8 )

	drawColor( wholePart , x , y , outputHeight , outputWidth , index , 1 )
	drawColor( singlePart , x , y , outputHeight , outputWidth , index , 1 )

	cv2.imwrite( "{}/{}_{}_whole.jpg".format( fileStoragePath , edge , part ) , wholePart )
	cv2.imwrite( "{}/{}_{}_{}.jpg".format( fileStoragePath , edge , part , bodyPartName[ index ] ) , singlePart )

def normalization( img , fileStoragePath , storeFileName , photoNumber , edge , part ):
	global color            # drawing color , definition line 59
	global datum         # openpose function call , definition line 35
	global opWrapper
	global bodyPartName     # csv file content english matching array
	global processNewPerson # use to check if new person , so new track photo needs to be generate
	global storageKeypoints # previous keypoints storage

	# print( '/'.join( fileStoragePath.split( '/' )[ :-2 ] ) )
	# # /media/ambersun/dataset_n/CASIA_n
	# sys.exit( 0 )



	outputWidth = 150
	outputHeight = 600

	height , width , channel = img.shape
	datum.cvInputData = img
	opWrapper.emplaceAndPop([datum])
	keypoints = datum.poseKeypoints
	output = datum.cvOutputData
	# keypoints , output = openpose.forward( img , True )

	numPeople , numKeypoints , trash = keypoints.shape
	if numPeople != 1:
		print( " , people = {}".format( numPeople ) , end = '' )

	# initial crop edges
	maxX = 0
	minX = width
	maxY = 0
	minY = height

	storageKeypoints = np.zeros( ( 25 , 2 ) ) # re-initialize the array

	# create new img if processing new people or new part
	if processNewPerson:
		normalizeTrackImg = np.ones( ( outputHeight , outputWidth , 3 ) , dtype = np.uint8 )
	else:
		normalizeTrackImg = cv2.imread( "{}/{}_n.jpg".format( fileStoragePath , storeFileName ) )

	# create store image
	normalizeImg = np.ones( ( outputHeight , outputWidth , 3 ) , dtype = np.uint8 )

	# open or create csv file
	try:
		with open( "{}/{}.csv".format( fileStoragePath , storeFileName ) , "a+" , newline = "" ) as csvFile:
			csv_writer = csv.writer( csvFile )

			csv_writer.writerow( [ "photo number" , photoNumber ] )
			csv_writer.writerow( [ " " , "x" , "y" ] )

			# iterate all keypoints
			for people in keypoints:
				colorCount = 0
				for points in people:
					x = math.floor( points[ 0 ] )
					y = math.floor( points[ 1 ] )
					confidence = points[ 2 ]

					# out of bound detect
					x = x if x >= 0 else 0
					y = y if y >= 0 else 0
					x = x if x < width else width - 1
					y = y if y < height else height - 1

					# get edges
					maxX = x if x > maxX and confidence != 0 else maxX
					minX = x if x < minX and confidence != 0 else minX
					maxY = y if y > maxY and confidence != 0 else maxY
					minY = y if y < minY and confidence != 0 else minY

					if storageKeypoints[ colorCount ][ 0 ] <= 0 and storageKeypoints[ colorCount ][ 1 ] <= 0:
						if confidence == 0:
							storageKeypoints[ colorCount ][ 0 ] = -1
							storageKeypoints[ colorCount ][ 1 ] = -1
						else:
							storageKeypoints[ colorCount ][ 0 ] = int( x )
							storageKeypoints[ colorCount ][ 1 ] = int( y )
					colorCount += 1

			minY = minY - 5 if minY - 5 > 0 else 0
			maxY = maxY + 5 if maxY + 5 < height else height - 1
			minX = minX - 5 if minX - 5 > 0 else 0
			maxX = maxX + 5 if maxX + 5 < width else width - 1

			edges = [ [ minY , minX ] , [ minY , maxX ] , [ maxY , minX ] , [ maxY , maxX ] ]
			# up left , up right , down left , down right

			# crop image to person size failed
			if maxY - minY - 1 < 0 or maxX - minX - 1 < 0:
				check = 1
			else:
				storageKeypoints = storageKeypoints.astype( int )

				extractHeight = maxY - minY
				extractWidth = maxX - minX

				probablyFailCount = 0
				for i in range( 0 , 25 ):

					if storageKeypoints[ i ][ 0 ] != -1 and storageKeypoints[ i ][ 1 ] != -1:
						# convert to relative coordinate ( origin photo
						storageKeypoints[ i ][ 0 ] = int( storageKeypoints[ i ][ 0 ] - minX )
						storageKeypoints[ i ][ 1 ] = int( storageKeypoints[ i ][ 1 ] - minY )

						# resize coordinate to normalize image
						storageKeypoints[ i ][ 0 ] = int( round( storageKeypoints[ i ][ 0 ] * ( outputWidth / extractWidth ) ) )
						storageKeypoints[ i ][ 1 ] = int( round( storageKeypoints[ i ][ 1 ] * ( outputHeight / extractHeight ) ) )
					else:
						probablyFailCount += 1

					# adjust height & width
					storageKeypoints[ i ][ 0 ] = storageKeypoints[ i ][ 0 ] if storageKeypoints[ i ][ 0 ] < outputWidth else outputWidth -1
					storageKeypoints[ i ][ 1 ] = storageKeypoints[ i ][ 1 ] if storageKeypoints[ i ][ 1 ] < outputHeight else outputHeight -1

					# write to csv
					csv_writer.writerow( [ bodyPartName[ i ] , storageKeypoints[ i ][ 0 ] , storageKeypoints[ i ][ 1 ] ] )

					if storageKeypoints[ i ][ 0 ] != -1 and storageKeypoints[ i ][ 1 ] != -1:
						# write to img
						drawColor( normalizeImg , storageKeypoints[ i ][ 0 ] , storageKeypoints[ i ][ 1 ] , outputHeight , outputWidth , i , 3 )
						drawColor( normalizeTrackImg , storageKeypoints[ i ][ 0 ] , storageKeypoints[ i ][ 1 ] , outputHeight , outputWidth , i , 3 )

						drawSumPicture( '/'.join( fileStoragePath.split( '/' )[ :-2 ] ) , edge , part , storageKeypoints[ i ][ 0 ] , storageKeypoints[ i ][ 1 ] , outputHeight , outputWidth , i )

				if numPeople != 1:
					check = 2
				elif probablyFailCount < 17:
					check = 0
				else:
					check = 3

				cv2.imwrite( "{}/{}_n.jpg".format( fileStoragePath , photoNumber ) , normalizeImg )
				cv2.imwrite( "{}/{}_n.jpg".format( fileStoragePath , storeFileName ) , normalizeTrackImg )
	# if open a file have a problem
	except IOError as e:
		print( e )
		return 4

	return check

if __name__ == "__main__":
	# iterate all dataset image
	sourcePath = "/home/louisme/PycharmProjects/basketBallDataset/layup"

	# expanduser e.g. "~/dataset" => "/home/ambersun/dataset"
	sourcePath = os.path.expanduser( sourcePath )

	if not os.path.isdir( sourcePath ):
		print( "invalid directory , abort" )
		sys.exit( 1 )

	print( "full source path: {}".format( sourcePath ) )
	prefixPath = os.path.dirname( sourcePath )

	# .csv file filename variable
	storeFileName = ""

	# detect new person or new part
	processNewPerson = False

	for roots , dirs , files in os.walk( sourcePath ):
		for filename in sorted( files ):
			# get filename full path
			filename = os.path.join( roots , filename )

			# get file relative path e.g. data/person......
			filename = os.path.relpath( filename , prefixPath )

			# because filename path have been change to relative path , so need to bring back for imread
			originalFileLocation = os.path.join( prefixPath , filename )

			# split relative path , for creating dynamic directory name
			temp = filename.split( os.sep )

			# creating normalize path with "_n" and process image
			fileStoragePath = os.path.join( prefixPath , temp[ 0 ] )
			fileStoragePath = os.path.join( fileStoragePath , temp[ 1 ] + "_n" )
			fileStoragePath = os.path.join( fileStoragePath , temp[ 2 ] + "_n" )

			# temp[ 0 ] = throwBall
			# temp[ 1 ] = videos
			# temp[ 2 ] = 001
			# temp[ 3 ] = 001.jpg

			# check storage filename is the same as previous , and change filename if different person
			if storeFileName != ( temp[ 2 ] + "_n"):
				processNewPerson = True
				storeFileName = temp[ 2 ] + "_n"

			# create normalize directory if not exists
			if not os.path.exists( fileStoragePath ):
				try:
					os.makedirs( fileStoragePath )
				except OSError as e:
					if e.errno != errno.EEXIST:
						raise

			# make normalization
			img = cv2.imread( originalFileLocation )
			if img is None:
				print( "{} file read failed".format( originalFileLocation ) )
				readFailed.append( originalFileLocation )
				readFailedCount += 1
				continue

			# fileStoragePath = e.g. Dataset/data_n/person007_n/
			# os.path.splitext( temp[ 4 ] )[ 0 ] => extract filename & it's extension
			if os.path.isfile( "{}/{}_n.jpg".format( fileStoragePath , os.path.splitext( temp[ 3 ] )[ 0 ] ) ):
				print( "file {} already normalized".format( filename ) )
				continue
			else:
				print( "now processing: {}".format( filename ) , end = '' )

			# normalization function
			# fileStoragePath = /media/ambersun/Dataset/data_n/person003_n/part1_n
			# storeFilename = person003_part1_n
			check = normalization( img , fileStoragePath , storeFileName , os.path.splitext( temp[ 3 ] )[ 0 ] , temp[ 1 ] , temp[ 2 ] )

			print() # important!!!

			if check == 1:
				print( "{} crop failed".format( filename ) )
				cropFailed.append( filename )
				cropFailedCount += 1
			elif check == 2:
				print( "{} person failed".format( filename ) )
				personFailed.append( filename )
				personFailedCount += 1
			elif check == 3:
				print( "{} keypoint failed".format( filename ) )
				keypointFailed.append( filename )
				keypointFailedCount += 1

			processNewPerson = False

	# redirect stdout to both console & log file
	sys.stdout = Logger()

	print( "\n---done---" ) # new line
	if readFailedCount != 0:
		print( "read failed" )
		for i in range( len( readFailed ) ):
			print( "\t{}".format( readFailed[ i ] ) )
		print()
	if cropFailedCount != 0:
		print( "crop failed" )
		for i in range( len( cropFailed ) ):
			print( "\t{}".format( cropFailed[ i ] ) )
		print()
	if personFailedCount != 0:
		print( "person failed( wrong person number , \"may error\" )")
		for i in range( len( personFailed ) ):
			print( "\t{}".format( personFailed[ i ] ) )
		print()
	if keypointFailedCount != 0:
		print( "keypoint failed( missing too much keypoints )" )
		for i in range( len( keypointFailed ) ):
			print( "\t{}".format( keypointFailed[ i ] ) )
		print()

	sys.exit( 0 )
