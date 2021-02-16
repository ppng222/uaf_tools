## IPK BUILDER (v0.1) ##
# This script will PACK map ipks only
# Made to replace unpakke, as target-specific building is required

import os
import struct
import sys
assert sys.version_info >= (3, 0)
from BundleFile import BundleFile
import time

def buildIPKWithParameters(platform,rootInput,output):
	startTime = time.time()
	BundleIPK = BundleFile(platform,output)		
	BundleIPK.setRootFolder(rootInput)
	BundleIPK.setPlatformSpecificFormats()
	BundleIPK.getAllFilesFromRoot()
	BundleIPK.determinePlatformSpecificFiles()
	BundleIPK.determineCookedFiles()
	BundleIPK.cookFiles()
	BundleIPK.createFileHeaderList()
	BundleIPK.serializeFilePackMaster()
	BundleIPK.createBundleBootHeader()
	BundleIPK.serializeBundleBootHeader()
	BundleIPK.writeBundleBootHeader()
	BundleIPK.writeFilePackMaster()
	BundleIPK.writeFilesToBundle()
	BundleIPK.close()
	endTime = time.time()
	print("Build took {} seconds".format(endTime-startTime))
def main():
	print("UBIART IPK BUILDER v0.0")
	print("Created by planedec50")
	print()
	print("The following platforms are supported: NX, WII, WIIU, X360, PC")
	platform = input("Console: ")
	rootInput = input("Folder to Pack: ")
	output = input("Output IPK: ")
	buildIPKWithParameters(platform,rootInput,output)
main()