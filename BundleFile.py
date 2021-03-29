import os
import struct
import sys
import glob
import json
from io import BytesIO
from ubisoftcrc import crc32
import time
import datetime
import shutil
import zlib
from xml.dom import minidom
import ubiartobjectfactory as uaf
from CSerializerObject import CSerializerObject
from Platform import Platform
from FileHeader import FileHeader
from Texture import Texture
from TextureCooker import TextureCooker
import AudioCooker
import TapeCooker

class BundleFile:
	def __init__(self,platformType,BundleOut):
		# initialize to default values
		self.MagicNumber = 1357648570 # unsigned int version of magic
		self.Version = 5
		self.PlatformSupported = Platform.getID(platformType) # use platform lookup for this
		self.FilesStart = 0x30 # value for NO FILES
		self.FilesCount = 0
		self.Compressed = 0
		self.BinaryScene = 0
		self.BinaryLogic = 0
		self.DataSignature = 0 # is this a crc or something?
		self.EngineSignature = crc32('planedec50')
		self.EngineVersion = crc32('JUSTDANCEHITS')
		self.OUTPUT = open(BundleOut,'wb')
		self.OUTPUT_FOLDER = BundleOut
		self.FILES = []
		self.ABSOLUTE_FILES = []
		self.PLATFORM = platformType
	def close(self):
		self.OUTPUT.close()
	def setBundleFiles(self,givenFiles):
		self.FILES = givenFiles
	def setRootFolder(self,rootFolder):
		if rootFolder[-1] == "\\" or rootFolder[-1] == "/":
			self.RootFolder = rootFolder
		else:
			self.RootFolder = rootFolder + '\\'
	def cookFiles(self):
		
		if self.PLATFORM == "NX":
			for currentFile in list(self.CookFiles):
				absOrigFilePath = self.CookFiles[currentFile]['rawFilePath']
				absFinalFilePath = self.CookFiles[currentFile]['filePath']
				## check if cooked file already exists ##
				if os.path.exists(absFinalFilePath): # check last modified date to see if the original file has changed
					# the file exists, check its last modified #
					origFileModTime = int(os.path.getmtime(absOrigFilePath))
					newFileModTime = int(os.path.getmtime(absFinalFilePath))
					if origFileModTime == newFileModTime: # THE FILE HAS NOT CHANGED ##
						continue  # break this iteration, do not cook the file
				## the actual cooking process ##
				fileDirectory = os.path.split(absFinalFilePath)[0].lower()
				fileExtension = os.path.splitext(absOrigFilePath)[1]
				# check if the FOLDER exists and make it if it doesnt
				if os.path.exists(fileDirectory) == False:
					os.makedirs(fileDirectory)
				# cook the file based on its extension
				if fileExtension == '.png' or fileExtension == '.tga':
					TextureCooker.textureCook(self.PLATFORM,absOrigFilePath,absFinalFilePath)
				
				elif fileExtension == '.wav':
					format = 'Nx  '
					if os.path.split(absOrigFilePath)[0].split(os.sep)[-1] == 'amb': 
						format = 'pcm '
					AudioCooker.convertToAudio(absOrigFilePath,absFinalFilePath,self.PLATFORM,format)
				elif fileExtension == '.dtape':
					TapeCooker.cookToPlatform(absOrigFilePath,absFinalFilePath,self.PLATFORM)
				elif fileExtension == '.act':
					XML = minidom.parse(open(absOrigFilePath,'r'))
					fileData = uaf.binaryActor(XML,self.PLATFORM)
					with open(absFinalFilePath,'wb') as ckdFile:
						ckdFile.write(fileData.getvalue())
				else:
					shutil.copyfile(absOrigFilePath,absFinalFilePath)
				## set the last modified date !!!! ##
				print("Cooking {}".format(currentFile))
				origFileModTime = int(os.path.getmtime(absOrigFilePath))
				os.utime(absFinalFilePath,(origFileModTime,origFileModTime))
		elif self.PLATFORM == "ORBIS" or self.PLATFORM == "PC":
			for currentFile in list(self.CookFiles):
				absOrigFilePath = self.CookFiles[currentFile]['rawFilePath']
				absFinalFilePath = self.CookFiles[currentFile]['filePath']
				## check if cooked file already exists ##
				if os.path.exists(absFinalFilePath): # check last modified date to see if the original file has changed
					# the file exists, check its last modified #
					origFileModTime = int(os.path.getmtime(absOrigFilePath))
					newFileModTime = int(os.path.getmtime(absFinalFilePath))
					if origFileModTime == newFileModTime: # THE FILE HAS NOT CHANGED ##
						continue  # break this iteration, do not cook the file
				## the actual cooking process ##
				fileDirectory = os.path.split(absFinalFilePath)[0].lower()
				fileExtension = os.path.splitext(absOrigFilePath)[1]
				# check if the FOLDER exists and make it if it doesnt
				if os.path.exists(fileDirectory) == False:
					os.makedirs(fileDirectory)
				# cook the file based on its extension
				if fileExtension == '.png' or fileExtension == '.tga':
					TextureCooker.textureCook(self.PLATFORM,absOrigFilePath,absFinalFilePath)
				
				elif fileExtension == '.wav':
					format = 'pcm '
					AudioCooker.convertToAudio(absOrigFilePath,absFinalFilePath,self.PLATFORM,format)
				elif fileExtension == '.dtape':
					TapeCooker.cookToPlatform(absOrigFilePath,absFinalFilePath,self.PLATFORM)
				elif fileExtension == '.act':
					XML = minidom.parse(open(absOrigFilePath,'r'))
					fileData = uaf.binaryActor(XML,self.PLATFORM)
					with open(absFinalFilePath,'wb') as ckdFile:
						ckdFile.write(fileData.getvalue())
				else:
					shutil.copyfile(absOrigFilePath,absFinalFilePath)
				## set the last modified date !!!! ##
				print("Cooking {}".format(currentFile))
				origFileModTime = int(os.path.getmtime(absOrigFilePath))
				os.utime(absFinalFilePath,(origFileModTime,origFileModTime))
		elif self.PLATFORM == "WIIU":
			for currentFile in list(self.CookFiles):
				absOrigFilePath = self.CookFiles[currentFile]['rawFilePath']
				absFinalFilePath = self.CookFiles[currentFile]['filePath']
				## check if cooked file already exists ##
				if os.path.exists(absFinalFilePath): # check last modified date to see if the original file has changed
					# the file exists, check its last modified #
					origFileModTime = int(os.path.getmtime(absOrigFilePath))
					newFileModTime = int(os.path.getmtime(absFinalFilePath))
					if origFileModTime == newFileModTime: # THE FILE HAS NOT CHANGED ##
						continue  # break this iteration, do not cook the file
				## the actual cooking process ##
				fileDirectory = os.path.split(absFinalFilePath)[0].lower()
				fileExtension = os.path.splitext(absOrigFilePath)[1]
				# check if the FOLDER exists and make it if it doesnt
				if os.path.exists(fileDirectory) == False:
					os.makedirs(fileDirectory)
				# cook the file based on its extension
				if fileExtension == '.png' or fileExtension == '.tga':
					TextureCooker.textureCook(self.PLATFORM,absOrigFilePath,absFinalFilePath)
				
				elif fileExtension == '.wav':
					format = 'adpc'
					interleave = True
					if os.path.split(absOrigFilePath)[0].split(os.sep)[-1] == 'amb': 
						interleave = False
					AudioCooker.convertToAudio(absOrigFilePath,absFinalFilePath,self.PLATFORM,format,interleave)
				elif fileExtension == '.dtape':
					TapeCooker.cookToPlatform(absOrigFilePath,absFinalFilePath,self.PLATFORM)
				elif fileExtension == '.act':
					XML = minidom.parse(open(absOrigFilePath,'r'))
					fileData = uaf.binaryActor(XML,self.PLATFORM)
					with open(absFinalFilePath,'wb') as ckdFile:
						ckdFile.write(fileData.getvalue())
				else:
					shutil.copyfile(absOrigFilePath,absFinalFilePath)
				## set the last modified date !!!! ##
				print("Cooking {}".format(currentFile))
				origFileModTime = int(os.path.getmtime(absOrigFilePath))
				os.utime(absFinalFilePath,(origFileModTime,origFileModTime))
		elif self.PLATFORM == "WII":
			tapeExtensions = ['.dtape','.ktape','.tape']
			for currentFile in list(self.CookFiles):
				absOrigFilePath = self.CookFiles[currentFile]['rawFilePath']
				absFinalFilePath = self.CookFiles[currentFile]['filePath']
				## check if cooked file already exists ##
				if os.path.exists(absFinalFilePath): # check last modified date to see if the original file has changed
					# the file exists, check its last modified #
					origFileModTime = int(os.path.getmtime(absOrigFilePath))
					newFileModTime = int(os.path.getmtime(absFinalFilePath))
					if origFileModTime == newFileModTime: # THE FILE HAS NOT CHANGED ##
						continue  # break this iteration, do not cook the file
				## the actual cooking process ##
				fileDirectory = os.path.split(absFinalFilePath)[0].lower()
				fileExtension = os.path.splitext(absOrigFilePath)[1]
				# check if the FOLDER exists and make it if it doesnt
				if os.path.exists(fileDirectory) == False:
					os.makedirs(fileDirectory)
				# cook the file based on its extension
				if fileExtension == '.png' or fileExtension == '.tga':
					TextureCooker.textureCook(self.PLATFORM,absOrigFilePath,absFinalFilePath)
				
				elif fileExtension == '.wav':
					format = 'adpc'
					interleave = True
					if os.path.split(absOrigFilePath)[0].split(os.sep)[-1] == 'amb': 
						interleave = False
					AudioCooker.convertToAudio(absOrigFilePath,absFinalFilePath,self.PLATFORM,format,interleave)
				elif fileExtension in tapeExtensions:
					TapeCooker.cookToPlatform(absOrigFilePath,absFinalFilePath,self.PLATFORM)
				elif fileExtension == '.act':
					XML = minidom.parse(open(absOrigFilePath,'r'))
					fileData = uaf.binaryActor(XML,self.PLATFORM)
					with open(absFinalFilePath,'wb') as ckdFile:
						ckdFile.write(fileData.getvalue())
				elif fileExtension == '.isc':
					XML = minidom.parse(open(absOrigFilePath,'r'))
					Root = uaf.findNodes(XML,'root')[0]
					scene = uaf.findNodes(Root,'Scene')[0]
					with open(absFinalFilePath,'wb') as ckdFile:
						uaf.Scene(ckdFile,scene)
				elif fileExtension == '.tpl':
					jsonData = json.loads(open(absOrigFilePath,'r').read().strip('\x00'))
					with open(absFinalFilePath,'wb') as ckdFile:
						uaf.JSON_Serialize(ckdFile,jsonData,"2016")
				else:
					print(f"unknown or non-serializable file: {currentFile}")
					shutil.copyfile(absOrigFilePath,absFinalFilePath)
				## set the last modified date !!!! ##
				print("Cooking {}".format(currentFile))
				origFileModTime = int(os.path.getmtime(absOrigFilePath))
				os.utime(absFinalFilePath,(origFileModTime,origFileModTime))
	def determineCookedFiles(self):	
		cookExtensions = [".wav", ".png", ".tga", ".tape", ".dtape", ".ktape", ".isc", ".tpl", ".msh", ".act", ".mpd", ".sgs"]
		compressExtensions = [".png", ".tga", ".m3d"]
		self.CookFiles = {}
		for currentFile in list(self.FILES):
			fileExt = os.path.splitext(currentFile)[1]
			if fileExt in cookExtensions:
				if fileExt in compressExtensions:
					compress = True
				else:
					compress = False
				relativeCacheFile = "cache\itf_cooked\{}\{}.ckd".format(self.PLATFORM,currentFile)
				absCacheFile = "{}cache\itf_cooked\{}\{}.ckd".format(self.RootFolder,self.PLATFORM,currentFile)
				fileData = {
					"filePath": absCacheFile,
					"rawFilePath": self.FILES[currentFile]['filePath'], # the uncooked file, so we can cook later
					"compress": compress
				}
				self.CookFiles[relativeCacheFile] = fileData
				del self.FILES[currentFile]
		self.FILES.update(self.CookFiles)
	def setPlatformSpecificFormats(self):
		if self.PLATFORM == "NX":
			self.texFormat = "XTX"
			self.audioFormat = "NX_OGG"
			self.ambFormat = "PCM"
			self.videoDef = ".vp9.720"
			self.serializer = "TEXT"
		elif self.PLATFORM == "PC":
			self.texFormat = "DDS"
			self.audioFormat = "PCM"
			self.ambFormat = "PCM"
			self.videoDef = ""
			self.serialize = "TEXT"
		elif self.PLATFORM == "WIIU":
			self.texFormat = "GTX"
			self.audioFormat = "ADPC"
			self.ambFormat = "ADPC_AMB"
			self.videoDef = ""
			self.serialize = "TEXT"
		elif self.PLATFORM == "WII":
			self.texFormat = "WII"
			self.audioFormat = "ADPC"
			self.ambFormat = "ADPC_AMB"
			self.videoDef = ".wii"
			self.serialize = "BINARY"
		elif self.PLATFORM == "X360":
			self.texFormat = "XPR"
			self.audioFormat = "XMA2"
			self.ambFormat = "XMA2"
			self.videoDef = ".x360"
			self.serialize = "BINARY"
	def determinePlatformSpecificFiles(self):
		## platform specific files are cooked only for the specified platform
		## the other files must be removed, usually just webms in world
		for currentFile in list(self.FILES):
			## just iterate through and check all webms
			fileExt = os.path.splitext(currentFile)[1]
			if fileExt == ".webm":
				videoDef = os.path.splitext(os.path.splitext(os.path.splitext(currentFile)[0])[0])[1] + os.path.splitext(os.path.splitext(currentFile)[0])[1]
				if videoDef != self.videoDef:
					del self.FILES[currentFile]
			elif fileExt == ".msm" or fileExt == ".gesture":
				platformFolder = os.path.split(currentFile)[0].split(os.sep)[-1].upper()
				if (platformFolder != self.PLATFORM) and (platformFolder != 'WIIU'):
					del self.FILES[currentFile]
	def getAllFilesFromRoot(self):
		ABSOL_FILES = glob.glob('{}\world\**\*.*'.format(self.RootFolder),recursive=True) + glob.glob('{}\cache\itf_cooked\{}\**\*.*'.format(self.RootFolder,self.PLATFORM),recursive=True)
		FILES = {}
		for currentFile in ABSOL_FILES:
			## check for desktop.ini ##
			## why does it even show up smh ##
			if currentFile[-11:] == "desktop.ini":
				continue ## dont do anything with the file just pass over it
			else:
				## this is not a desktop.ini file ##
				relativeFilePath = currentFile[len(self.RootFolder)+1:]
				## check if this is a shortcut file ##
				if currentFile[-13:] == ".__SHORTCUT__":
					with open(currentFile,'rb') as fileHandle:
						absPath = fileHandle.read().decode()
				else:
					absPath = currentFile
				fileData = {
					"filePath": os.path.normpath(absPath),
					"compress": False
				}
				FILES[os.path.normpath(relativeFilePath)] = fileData
		self.FILES = FILES
	def serializeBundleBootHeader(self):
		self.BundleBootHeaderSerialized = BytesIO()
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.MagicNumber)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.Version)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.PlatformSupported)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.FilesStart)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.FilesCount)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.Compressed)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.BinaryScene)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.BinaryLogic)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.DataSignature)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.EngineSignature)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.EngineVersion)
		CSerializerObject.uint32(self.BundleBootHeaderSerialized,self.FilesCount)
	def createFileHeaderList(self):
		self.FileHeaderList = []
		for currentFile in list(self.FILES):
			FileObject = FileHeader(currentFile,self.FILES[currentFile]['filePath'],self.RootFolder,self.FILES[currentFile]['compress'])
			self.FileHeaderList.append(FileObject)
	def createBundleBootHeader(self):
		## just set all vars that changed after object was created
		self.FilesStart = self.FilePackSerialized.getbuffer().nbytes + self.FilesStart
		self.FilesCount = len(self.FILES.keys())
	def serializeFilePackMaster(self):
		# we need to determine each files offset!
		FilePackOffset = 0
		self.FilePackSerialized = BytesIO()
		for i in range(len(self.FileHeaderList)):
			self.FileHeaderList[i].offset = FilePackOffset
			## do we get compressed file size? or regular filesize ##
			if self.FileHeaderList[i].compress == True:
				currentFileSize = self.FileHeaderList[i].CompressedSize
			else:
				currentFileSize = self.FileHeaderList[i].OriginalSize
			self.FileHeaderList[i].serialize()
			FilePackOffset += currentFileSize
			self.FilePackSerialized.write(self.FileHeaderList[i].outputIO.getvalue())
	def writeFilePackMaster(self):
		## write data to actual bundle ##
		self.OUTPUT.write(self.FilePackSerialized.getvalue())
	def writeBundleBootHeader(self):
		self.OUTPUT.write(self.BundleBootHeaderSerialized.getvalue())
	def writeFilesToBundle(self):
		for i in range(len(self.FileHeaderList)):
			filePath = self.FileHeaderList[i].AbsolutePath
			compressFlag = self.FileHeaderList[i].compress
			## grab all the file data ##
			with open(filePath,'rb') as fileHandle:
				fileData = fileHandle.read()
			## compress if needed ##
			if compressFlag == True:
				fileData = zlib.compress(fileData)
			
			
			print("Writing {}".format(self.FileHeaderList[i].Path))
			self.OUTPUT.write(fileData)