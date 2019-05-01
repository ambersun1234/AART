import os
import sys
from collections import OrderedDict

try:
	import matplotlib.pyplot as plt
except ImportError:
	print( "install matplotlib by using `sudo pip3 install matplotlib`" )
	sys.exit( 1 )

if __name__ == "__main__":
	sourceDirectory = "/media/ambersun/gitRepo/yolov3/labels/"
	jerseyNumber = dict()

	print( "checking directory valid..." , end = "" )
	if os.path.isdir( sourceDirectory ) and os.path.exists( sourceDirectory ):
		print( "yes" )
	else:
		print( "no" )

	# check classes.txt exists
	if os.path.isfile( "{}{}".format( sourceDirectory , "classes.txt" ) ):
		print( "classes.txt found\n" )
		try:
			classes = [ line.rstrip( '\n' ) for line in open( "{}{}".format( sourceDirectory , "classes.txt" ) , "r" ) ]
		except IOError:
			print( "error occurred , abort" )
			sys.exit( 1 )
	else:
		print( "classes.txt not found , abort" )
		sys.exit( 1 )

	# iterate all .txt file
	for roots , dirs , files in os.walk( sourceDirectory ):
		for file in files:
			if file == "classes.txt":
				break

			print( "{}{}".format( roots , file ) )
			try:
				for line in open( "{}{}".format( roots , file ) , "r" ):
					jerseyNumber[ classes[ ( int )( line.split( ' ' )[ 0 ] ) ] ] = jerseyNumber.get( classes[ ( int )( line.split( ' ' )[ 0 ] ) ] , 0 ) + 1
			except IOError:
				print( "file {}{} not exists".format( roots , file ) )
				sys.exit( 1 )

	jerseyNumber = ( OrderedDict )( sorted( jerseyNumber.items() , key = lambda x : int( x[ 0 ] ) ) )

	plt.bar( jerseyNumber.keys() , jerseyNumber.values() , 0.7 , color='b' )
	plt.xlabel( "jersey number" )
	plt.ylabel( "amount" )
	plt.show()