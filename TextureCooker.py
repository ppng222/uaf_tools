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
import shutil
from Texture import Texture
class TextureCooker:
	@staticmethod
	def ddsCook(inTexture,outTexture,compression,mips=None):
		nvcompress = r"F:\JDHits_MASTER\TOOLS\Bin\nvcompress.exe"
		## create args ##
		if compression == "DXT1":
			compType = "-bc1"
		elif compression == "DXT3":
			compType = "-bc2"
		elif compression == "DXT5":
			compType = "-bc3"
		elif compression == "RGBA32":
			compType = "-rgb"
		os.system("{} -silent -nomips -nocuda {} {} {}".format(nvcompress,compType,inTexture,outTexture))
	@staticmethod
	def pcCook(inTexture,outTexture):
		pcTexture = Texture(inTexture,outTexture,"PC")
		pcTexture.getDummyHeader()
		pcTexture.determineTextureData()
		pcTexture.ddsCook()
		pcTexture.serializeTextureHeader()
		pcTexture.writeTextureCKD()
		del pcTexture
	@staticmethod
	def nxCook(inTexture,outTexture):
		nxTexture = Texture(inTexture,outTexture,"NX")
		nxTexture.getDummyHeader()
		nxTexture.determineTextureData()
		nxTexture.xtxCook()
		nxTexture.serializeTextureHeader()
		nxTexture.writeTextureCKD()
		del nxTexture
	@staticmethod
	def wiiuCook(inTexture,outTexture):
		wiiuTexture = Texture(inTexture,outTexture,"WIIU")
		wiiuTexture.getDummyHeader()
		wiiuTexture.determineTextureData()
		wiiuTexture.gtxCook()
		wiiuTexture.serializeTextureHeader()
		wiiuTexture.writeTextureCKD()
		del wiiuTexture
	def wiiCook(inTexture,outTexture):
		wiiTexture = Texture(inTexture,outTexture,"WII")
		wiiTexture.getDummyHeader()
		wiiTexture.determineTextureData()
		wiiTexture.wiiCook()
		wiiTexture.serializeTextureHeader()
		wiiTexture.writeTextureCKD()
		del wiiTexture
	@staticmethod
	def textureCook(platformType,inTexture,outTexture):
		## for some reason, wiiu/xtx cookers cant handle the wrong extensions, copy them to temp folder ##
		FLAG_CONV_TO_DDS = False
		if os.path.isdir('C:\\temp\\') == False:
				os.mkdir('C:\\temp\\')
		## this will cook a given texture and output it to the outTexture ##
		
		## check if the given file is already dds ##
		with open(inTexture,'rb') as texFile:
			if texFile.read(4) != b"DDS ":
				print("THIS FILE IS NOT DDS")
				print(inTexture)
				raise TypeError("This is not a DDS file")
			else:
				texFile.seek(0x54,0)
				compression = texFile.read(4)
				if compression == b'\x00\x00\x00\x00':
					compression = 'RGBA32'
		if platformType == "NX":
			## determine temp file and output file ##
			tmpDDS = 'C:/temp/temp.dds'
			shutil.copy(inTexture,tmpDDS)
			inTexture = tmpDDS
			TextureCooker.nxCook(inTexture,outTexture)
		elif platformType == "WIIU":
			tmpDDS = 'C:/temp/temp.dds'
			shutil.copy(inTexture,tmpDDS)
			inTexture = tmpDDS
			TextureCooker.wiiuCook(inTexture,outTexture)
		elif platformType == "WII":
			## so for some reason wimgt doesnt support dds, so convert to png instead ##
			if FLAG_CONV_TO_DDS:
				tmpDDS = 'C:/temp/temp.dds'
				TextureCooker.ddsCook(inTexture,tmpDDS,compression)
				inTexture = tmpDDS
			TextureCooker.wiiCook(inTexture,outTexture)
		elif platformType == "PC" or platformType == "ORBIS":
			TextureCooker.pcCook(inTexture,outTexture)
		## remove tmp folder ##
		shutil.rmtree('C:/temp')