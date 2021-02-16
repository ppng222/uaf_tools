import os
import struct
import sys
import glob
from io import BytesIO
from ubisoftcrc import crc32
from PIL import Image
import numpy

class Platform:
	@staticmethod
	def getString(platNumber):
		platforms = {0:"PC",1:"X360",2:"PS3",3:"ORBIS",4:"CTR",5:"WII",6:"EMUWII",7:"VITA",8:"WIIU",9:"IPAD",0xA:"DURANGO",0xB:"NX"}
		try:
			returnString = platformByNumber[platNumber]
		except:
			returnString = 'Invalid platform'
		return returnString
	@staticmethod
	def getID(platNumber):
		platformByString={"PC":0,"X360":1,"PS3":2,"ORBIS":3,"CTR":4,"WII":5,"EMUWII":6,"VITA":7,"WIIU":8,"IPAD":9,"DURANGO":0xA,"NX":0xB}
		try:
			returnString = platformByString[platNumber]
		except:
			returnString = -1
		return returnString