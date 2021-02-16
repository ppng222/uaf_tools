import os
import struct
import sys
import glob
from io import BytesIO
from ubisoftcrc import crc32
from PIL import Image
import numpy

class CSerializerObject:
	@staticmethod
	def rawBytes(fileHandle,s):
		## write raw bytes to the file handle ##
		fileHandle.write(s)
	@staticmethod
	def manual(fileHandle,s,packFormat):
		## the user wants to manually pack bytes ##
		if packFormat != 'raw':
			encodeFormat = '>{}'.format(packFormat)
			fileHandle.write(struct.pack(encodeFormat,s))
		else:
			## the user wants to write raw data ##
			fileHandle.write(s)
	@staticmethod
	def ubyte(fileHandle,s):
		fileHandle.write(struct.pack('>B',s))
	@staticmethod
	def byte(fileHandle,s):
		fileHandle.write(struct.pack('>b',s))
	@staticmethod
	def ushort(fileHandle,s):
		fileHandle.write(struct.pack('>H',s))
	@staticmethod
	def short(fileHandle,s):
		fileHandle.write(struct.pack('>h',s))
	@staticmethod
	def uint32(fileHandle,s):
		fileHandle.write(struct.pack('>I',s))
	@staticmethod
	def int32(fileHandle,s):
		fileHandle.write(struct.pack('>i',s))
	@staticmethod
	def ulong(fileHandle,s):
		fileHandle.write(struct.pack('>Q',s))
	@staticmethod
	def long(fileHandle,s):
		fileHandle.write(struct.pack('>q',s))
	@staticmethod
	def Path(fileHandle,s):
		flag = 0
		folder = os.path.split(s)[0]
		if len(s) != 0:
			folder = folder + '/'
		file = os.path.split(s)[1]
		fileHandle.write(struct.pack('>I',len(file)))
		fileHandle.write(bytes(file.encode('utf-8')))
		fileHandle.write(struct.pack('>I',len(folder)))
		fileHandle.write(bytes(folder.encode('utf-8')))
		fileHandle.write(struct.pack('>I',crc32(s)))
		fileHandle.write(struct.pack('>I',flag))
		
class CSerializerObject_LE:
	@staticmethod
	def rawBytes(fileHandle,s):
		## write raw bytes to the file handle ##
		fileHandle.write(s)
	@staticmethod
	def manual(fileHandle,s,packFormat):
		## the user wants to manually pack bytes ##
		if packFormat != 'raw':
			encodeFormat = '<{}'.format(packFormat)
			
			fileHandle.write(struct.pack(encodeFormat,s))
		else:
			## the user wants to write raw data ##
			fileHandle.write(s)
	@staticmethod
	def ubyte(fileHandle,s):
		fileHandle.write(struct.pack('<B',s))
	@staticmethod
	def byte(fileHandle,s):
		fileHandle.write(struct.pack('<b',s))
	@staticmethod
	def ushort(fileHandle,s):
		fileHandle.write(struct.pack('<H',s))
	@staticmethod
	def short(fileHandle,s):
		fileHandle.write(struct.pack('<h',s))
	@staticmethod
	def uint32(fileHandle,s):
		fileHandle.write(struct.pack('<I',s))
	@staticmethod
	def int32(fileHandle,s):
		fileHandle.write(struct.pack('<i',s))
	@staticmethod
	def ulong(fileHandle,s):
		fileHandle.write(struct.pack('<Q',s))
	@staticmethod
	def long(fileHandle,s):
		fileHandle.write(struct.pack('<q',s))