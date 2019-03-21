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
	net = load_net( b"./src/jerseyNumber.cfg" , b"./weights/yolov3_210000.weights" , 0 )
	meta = load_meta( b"./src/obj.data" )

	number = "0001"

	frame = cv2.imread( "./images/{}.png".format( number ) )

	result = detect( net , meta , frame )

	for i in result :
		print( i )
		x , y , w , h = i[ 2 ][ 0 ] , i[ 2 ][ 1 ] , i[ 2 ][ 2 ] , i[ 2 ][ 3 ]
		xmin , ymin , xmax , ymax = convertBack( float( x ) , float( y ) , float( w ) , float( h ) )
		pt1 = ( xmin , ymin )
		pt2 = ( xmax , ymax )
		cv2.rectangle( frame , pt1 , pt2 , (0 , 255 , 0) , 2 )

		cv2.putText( frame , i[ 0 ].decode() + " [" + str( round( i[ 1 ] * 100 , 2 ) ) + "]" ,
					( pt1[ 0 ] - 30 , pt1[ 1 ] - 10 ) ,
					cv2.FONT_HERSHEY_SIMPLEX ,
					1 , [ 0 , 255 , 0 ] , 4 )

	cv2.imshow( "output" , frame )
	cv2.imwrite( "./images/{}_out.png".format( number ) , frame )
	cv2.waitKey( 0 )
	cv2.destroyAllWindows()
