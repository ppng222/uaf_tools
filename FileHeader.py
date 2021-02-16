import os
import struct
import sys
import glob
from io import BytesIO
from ubisoftcrc import crc32
from PIL import Image
import numpy
import zlib
from CSerializerObject import CSerializerObject
EPOCH_AS_FILETIME = 116444736000000000
HUNDREDS_OF_NANOSECONDS = 10000000
class FileHeader:
	def setOffset(self,offset):
		self.offset = offset
	def getFileSize(self,path):
		with open(path,"rb") as fileHandle:
			fileHandle.seek(0,2)
			return fileHandle.tell()
	def getCompressedFileSize(self,absPath,compress=False):
		# returns the files compress size, only is compress is set to true
		if compress == True:
			fileData = open(absPath,'rb').read()
			return len(zlib.compress(fileData))
		else:
			return 0
	def __init__(self,relativePath,absolutePath,rootFolder,compress=False):
		relativePath = relativePath.replace('\\','/')
		self.rootFolder = rootFolder
		self.numOffsets = 1 ## idk any instance where theres multiple offsets?
		self.OriginalSize = self.getFileSize(absolutePath)
		self.CompressedSize = self.getCompressedFileSize(absolutePath,compress) 
		self.TimeStamp = int(os.path.getmtime(absolutePath)*HUNDREDS_OF_NANOSECONDS+EPOCH_AS_FILETIME)
		self.offset = 0 ## this will be set by the BundleFile class
		self.AbsolutePath = absolutePath
		self.Path = relativePath.lower()
		self.compress = compress
	def debug__PrintItems(self):
		print(self.rootFolder)
		print(self.numOffsets)
		print(self.OriginalSize)
		print(self.CompressedSize)
		print(self.TimeStamp)
		print(self.offset)
		print(self.Path) 
	def serialize(self):
		self.outputIO = BytesIO()
		CSerializerObject.uint32(self.outputIO,self.numOffsets)
		CSerializerObject.uint32(self.outputIO,self.OriginalSize)
		CSerializerObject.uint32(self.outputIO,self.CompressedSize)
		CSerializerObject.ulong(self.outputIO,self.TimeStamp)
		CSerializerObject.ulong(self.outputIO,self.offset)
		CSerializerObject.Path(self.outputIO,self.Path)
	def serializeJSON(self):
		JSONObject = {
			"numOffsets": self.numOffsets,
			"OriginalSize": self.OriginalSize,
			"CompressedSize": self.CompressedSize,
			"TimeStamp": self.TimeStamp,
			"offset": self.offset,
			"Path": self.Path
		}
		return JSONObject