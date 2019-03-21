import xml.etree.ElementTree as ElementTree
import os
import sys
from collections import OrderedDict

try:
	import matplotlib.pyplot as plt
except ImportError:
	print( "install matplotlib by using `sudo pip3 install matplotlib`" )
	sys.exit( 1 )

if __name__ == "__main__":
	sourceDirectory = "/media/ambersun/trainingDatasets/labels/"
	jerseyNumber = dict()

	print( "checking directory valid..." , end = "" )
	if os.path.isdir( sourceDirectory ) and os.path.exists( sourceDirectory ):
		print( "yes" )
	else:
		print( "no" )

	for roots , dirs , files in os.walk( sourceDirectory ):
		for file in files:
			print( "{}{}".format( roots , file ) )
			try:
				with open( "{}{}".format( roots , file ) , "r" ) as xml:
					root = ElementTree.parse( xml ).getroot()
					for element in root.findall( "object" ):
						jerseyNumber[ element.find( "name" ).text ] = jerseyNumber.get( element.find( "name" ).text , 0 ) + 1

			except IOError:
				print( "file {}{} not exists".format( roots , file ) )
				sys.exit( 1 )

	jerseyNumber = ( OrderedDict )( sorted( jerseyNumber.items() , key = lambda x : int( x[ 0 ] ) ) )

	plt.bar( jerseyNumber.keys() , jerseyNumber.values() , 0.7 , color='b' )
	plt.xlabel( "jersey number" )
	plt.ylabel( "amount" )
	plt.show()