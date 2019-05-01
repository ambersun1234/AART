from darknet import *
import cv2
import sys
import openposeMy
import time

sys.path.append( '/usr/local/python/openpose' )
try :
	from openpose import *
except :
	raise Exception(
		'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python '
		'script in the right folder?' )
params = dict()
params[ "logging_level" ] = 3
params[ "output_resolution" ] = "-1x-1"
params[ "net_resolution" ] = "-1x368"
params[ "model_pose" ] = "BODY_25"
params[ "alpha_pose" ] = 0.6
params[ "scale_gap" ] = 0.3
params[ "scale_number" ] = 1
params[ "render_threshold" ] = 0.05
params[ "num_gpu_start" ] = 0
params[ "disable_blending" ] = False
params[ "default_model_folder" ] = "/home/ambersun/library/openpose/models/"
openpose = OpenPose( params )


def convertBack( x , y , w , h ) :
	xmin = int( round( x - (w / 2) ) )
	xmax = int( round( x + (w / 2) ) )
	ymin = int( round( y - (h / 2) ) )
	ymax = int( round( y + (h / 2) ) )
	return xmin , ymin , xmax , ymax


def openposeRect( x , y , w , h , ww , hh ) :
	xmin = int( round( x - (w / 2) * 10 ) ) if int( round( x - (w / 2) * 10 ) ) > 0 else 1
	xmax = int( round( x + (w / 2) * 10 ) ) if int( round( x + (w / 2) * 10 ) ) < ww else ww - 1
	ymin = int( round( y - (h / 2) * 10 ) ) if int( round( y - (h / 2) * 10 ) ) > 0 else 1
	ymax = int( round( y + (h / 2) * 10 ) ) if int( round( y + (h / 2) * 10 ) ) < hh else hh - 1
	return xmin , ymin , xmax , ymax


if __name__ == '__main__' :
	net = load_net( b"./src/yolov3.cfg" ,
					b"./weights/yolov3_20000.weights" , 0 )
	meta = load_meta( b"./src/obj.data" )
	capture = cv2.VideoCapture( './input/original.mp4' )

	fourcc = cv2.VideoWriter_fourcc( *'MJPG' )
	saving = cv2.VideoWriter( "out.mp4" , fourcc , 30.0 , (
		(int)( capture.get( cv2.CAP_PROP_FRAME_WIDTH ) ) , (int)( capture.get( cv2.CAP_PROP_FRAME_HEIGHT ) )) )

	jerseyNum = input( '輸入要追蹤的人的背號：' )

	while capture.isOpened() :
		startT = time.time()
		ret , frame = capture.read()

		# no image
		if not ret :
			break

		result = detect( net , meta , frame )

		for i in result :
			if not i[ 0 ].decode() == jerseyNum :
				continue

			x , y , w , h = i[ 2 ][ 0 ] , i[ 2 ][ 1 ] , i[ 2 ][ 2 ] , i[ 2 ][ 3 ]
			xmin , ymin , xmax , ymax = convertBack( float( x ) , float( y ) , float( w ) , float( h ) )
			xmiddle = (xmin + xmax) / 2
			pt1 = (xmin , ymin)
			pt2 = (xmax , ymax)
			cv2.rectangle( frame , pt1 , pt2 , (0 , 255 , 0) , 2 )

			hh , ww , cc = frame.shape
			ximin , yimin , ximax , yimax = openposeRect( x , y , w , h , ww , hh )
			print( yimin , " " , yimax , " " , ximin , " " , ximax )
			imgTmp = frame[ yimin : yimax , ximin : ximax ].copy()
			keypoints , out_img = openpose.forward( imgTmp , True )

			# for j in range(openposePersonNum):
			#     if keypoints[j][1][2] != 0 and keypoints[j][1][0] >= xmiddle - 50 and keypoints[j][1][0] <= xmiddle + 50
			#  and keypoints[j][1][1] >= ymin - 50 and keypoints[j][1][1] <= ymin + 50:
			#         frame = openposeMy.drawPerson(frame, keypoints[j])

			for person in keypoints:
				for points in person:
					points[ 0 ] += ximin
					points[ 1 ] += yimin
			for j in range( keypoints.shape[ 0 ] ):
				if keypoints[j][1][2] != 0 and keypoints[j][1][0] >= xmiddle - 50 and keypoints[j][1][0] <= xmiddle + 50 and keypoints[j][1][1] >= ymin - 50 and keypoints[j][1][1] <= ymin + 50:
					frame = openposeMy.drawPerson( frame , keypoints[ j ] )

			# put number & probability
			cv2.putText( frame , i[ 0 ].decode() + " [" + str( round( i[ 1 ] * 100 , 2 ) ) + "]" ,
						 ( pt1[ 0 ] + 30 , pt1[ 1 ] + 20 ) ,
						 cv2.FONT_HERSHEY_SIMPLEX ,
						 1 , [ 0 , 255 , 0 ] , 4 )

		endT = time.time()

		# put fps
		cv2.putText( frame , str( round( 1 / ( endT - startT ) , 2 ) ) , ( 15 , 25 ) , cv2.FONT_HERSHEY_PLAIN , 2 ,
					 (0 , 255 , 0) , 2 )

		# cv2.imshow( 'frame' , frame )
		saving.write( frame )
		q = cv2.waitKey( 1 )
		if q == ord( 'q' ) :
			break
		elif q == ord( 's' ) :
			cv2.waitKey( 0 )

	capture.release()
	saving.release()
	cv2.destroyAllWindows()
