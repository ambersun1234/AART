from darknet import *
import cv2


def convertBack( x , y , w , h ) :
	xmin = int( round( x - ( w / 2 ) ) )
	xmax = int( round( x + ( w / 2 ) ) )
	ymin = int( round( y - ( h / 2 ) ) )
	ymax = int( round( y + ( h / 2 ) ) )
	return xmin , ymin , xmax , ymax


if __name__ == "__main__" :
	# darknet setup
	net = load_net( b"./src/yolov3.cfg" , b"./weights/yolov3.weights" , 0 )
	meta = load_meta( b"./src/coco.data" )

	# setting up opencv
	capture = cv2.VideoCapture( "./video/b.mp4" )
	fourcc = cv2.VideoWriter_fourcc( *'MJPG' )

	saving = cv2.VideoWriter( "out.mp4" , fourcc , 20.0 , (
	(int)( capture.get( cv2.CAP_PROP_FRAME_WIDTH ) ) , (int)( capture.get( cv2.CAP_PROP_FRAME_HEIGHT ) )) )

	while capture.isOpened() :
		ret , frame = capture.read()

		if not ret :
			break

		result = detect( net , meta , frame )

		for i in result :
			if ( str )( i[ 0 ] ) != "b'person'" :
				continue

			print( i )
			x , y , w , h = i[ 2 ][ 0 ] , i[ 2 ][ 1 ] , i[ 2 ][ 2 ] , i[ 2 ][ 3 ]
			xmin , ymin , xmax , ymax = convertBack( float( x ) , float( y ) , float( w ) , float( h ) )
			pt1 = ( xmin , ymin )
			pt2 = ( xmax , ymax )
			cv2.rectangle( frame , pt1 , pt2 , (0 , 255 , 0) , 2 )

			# cv2.putText( frame , i[ 0 ].decode() + " [" + str( round( i[ 1 ] * 100 , 2 ) ) + "]" ,
			# 			( pt1[ 0 ] , pt1[ 1 ] + 20 ) ,
			# 		 	cv2.FONT_HERSHEY_SIMPLEX ,
			# 		 	1 , [ 0 , 255 , 0 ] , 4 )

		saving.write( frame )

	capture.release()
	saving.release()
	cv2.destroyAllWindows()
