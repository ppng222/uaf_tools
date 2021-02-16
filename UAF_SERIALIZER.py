import pyVerChecker
from UAF import UAF
import argparse
import os
import sys
parser = argparse.ArgumentParser(description='Serialize Just Dance Ubiart Files')
parser.add_argument('-g', action='store', dest='g', help='Game Type: 2014, 2015, or new (2016-2020)')
parser.add_argument('-f', action='store', dest='f', help='Origin Format Type (JSON,XML,BIN)')
parser.add_argument('-i', action='store', dest='i', help='Input file')
parser.add_argument('-o', action='store', dest='o', help='Output file')
args = vars(parser.parse_args())

if args['f'] == None:
	parser.print_help(sys.stderr)
	quit()
path, file = os.path.split(args['i'])
rawFileName, extension = os.path.splitext(file)
if extension != ".ckd":
	print("This file needs to end in .ckd in order to parse correctly!")
	quit()
else:
	fileName, uncookedExtension = os.path.splitext(rawFileName)
	if args['o'] != None:
		output = args['o']
	else:
		output = args['i'][:-4] ##current path with ckd extension
if args['f'] == "BIN":
	serialMode = 'serialFromBinary'
else:
	serialMode = 'serialToBinary'
	
SerializeObject = UAF(serialMode,args['g'],args['i'],output)
SerializeObject.SerializeImpl()