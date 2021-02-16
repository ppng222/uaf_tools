import os
import struct
import sys
import glob
from io import BytesIO
from ubisoftcrc import crc32
from PIL import Image
import numpy
from CSerializerObject import CSerializerObject
from Platform import Platform

class Texture:
	def __init__(self,ddsFile,outFile,platform):
		self.version = 9
		self.signature = 1413830656 #"TEX\x00"
		self.rawDataStartOffset = 0x500
		self.rawDataSize = 0
		self.width = 0
		self.height = 0
		self.depth = 1
		self.bpp = 32
		self.type = 0
		self.memorySize = 0
		self.uncompressedSize = 0
		self.nbOpaquePixels = 0
		self.nbHolePixels = 0
		self.wrapModeX = 2
		self.wrapModeY = 2
		self.dummybyte = 0
		self.dummybyte2 = 0
		self.dummyHEADER = None
		self.rawdata = None
		self.ddsPath = ddsFile
		self.outTexture = open(outFile,'wb')
		self.DDSTYPE = None
		self.platformType = platform
	def getDummyHeader(self):
		self.dummyHEADER = open(r"F:\JDHits_MASTER\TOOLS\Bin\texHeaders\{}.tex".format(self.platformType.lower()),'rb').read()
	def determineTextureData(self):
		mode_to_bpp = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
		## get dds format, necessary for wii
		with open(self.ddsPath,'rb') as fileHandle:
			fileHandle.seek(0x54)
			self.DDSTYPE = fileHandle.read(4)
			if self.DDSTYPE == b'\x00\x00\x00\x00':
				self.DDSTYPE = 'RGBA32'
			self.DDSTYPE = self.DDSTYPE.decode("utf-8")
		PIL_IMAGE = Image.open(self.ddsPath)
		self.width = PIL_IMAGE.width
		self.height = PIL_IMAGE.height
		self.bpp = mode_to_bpp[PIL_IMAGE.mode]
		## determine pixel amounts ##
		IMAGE_NP = numpy.array(PIL_IMAGE)
		for x in range(len(IMAGE_NP)):
			## X of pixel ##
			for y in range(len(IMAGE_NP[x])):
				# Y of X Row #
				if IMAGE_NP[x][y][3] == 0:
					self.nbHolePixels += 1
				elif IMAGE_NP[x][y][3] == 255:
					self.nbOpaquePixels += 1
	def xtxCook(self):
		textureCooker = r"F:\JDHits_MASTER\TOOLS\Bin\NvnTexpkg.exe"
		self.tmpCook = "C:/temp/textureTmp.xtx"
		os.system("{} -i {} -o {}".format(textureCooker,self.ddsPath,self.tmpCook))
		with open(self.tmpCook,'rb') as fileHandle:
			self.rawdata = fileHandle.read()
			self.rawDataSize = fileHandle.tell()
			self.memorySize = fileHandle.tell()
	def gtxCook(self):
		textureCooker = r"F:\JDHits_MASTER\TOOLS\Bin\TexConv2.exe"
		self.tmpCook = "C:/temp/textureTmp.gtx"
		os.system("{} -i {} -o {}".format(textureCooker,self.ddsPath,self.tmpCook))
		with open(self.tmpCook,'rb') as fileHandle:
			self.rawdata = fileHandle.read()
			self.rawDataSize = fileHandle.tell()
			self.memorySize = fileHandle.tell()
	def wiiCook(self):
		textureCooker = r"F:\JDHits_MASTER\TOOLS\Bin\cookWii.py"
		self.tmpCook = "C:/temp/textureTmp.ckd"
		os.system("py3 {} {} {} {}".format(textureCooker,self.ddsPath,self.tmpCook,str(self.DDSTYPE)))
		
		with open(self.tmpCook,'rb') as fileHandle:
			self.rawdata = fileHandle.read()
			self.rawDataSize = fileHandle.tell()
			self.memorySize = fileHandle.tell()
	def ddsCook(self):
		with open(self.ddsPath,'rb') as fileHandle:
			self.rawdata = fileHandle.read()
			self.rawDataSize = fileHandle.tell()
			self.memorySize = fileHandle.tell()
	def serializeTextureHeader(self):
		self.outputIO = BytesIO()
		CSerializerObject.uint32(self.outputIO,self.version)
		CSerializerObject.uint32(self.outputIO,self.signature)
		CSerializerObject.uint32(self.outputIO,self.rawDataStartOffset)
		CSerializerObject.uint32(self.outputIO,self.rawDataSize)
		CSerializerObject.ushort(self.outputIO,self.width)
		CSerializerObject.ushort(self.outputIO,self.height)
		CSerializerObject.ushort(self.outputIO,self.depth)
		CSerializerObject.ubyte(self.outputIO,self.bpp)
		CSerializerObject.ubyte(self.outputIO,self.type)
		CSerializerObject.uint32(self.outputIO,self.memorySize)
		CSerializerObject.uint32(self.outputIO,self.uncompressedSize)
		CSerializerObject.uint32(self.outputIO,self.nbOpaquePixels)
		CSerializerObject.uint32(self.outputIO,self.nbHolePixels)
		CSerializerObject.ubyte(self.outputIO,self.wrapModeX)
		CSerializerObject.ubyte(self.outputIO,self.wrapModeY)
		CSerializerObject.ubyte(self.outputIO,self.dummybyte)
		CSerializerObject.ubyte(self.outputIO,self.dummybyte2)
	def writeTextureCKD(self):
		self.outTexture.write(self.outputIO.getvalue())
		self.outTexture.write(self.dummyHEADER)
		self.outTexture.write(self.rawdata)
		self.outTexture.close()