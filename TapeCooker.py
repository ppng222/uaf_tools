import os
import json
import sys
## this script cooks a tape to a specified platforms required tape ##
class Tape:
	def __init__(self,dtapePath):
		self.TapeObject = json.load(open(dtapePath,'r'))
		self.Clips = []
	def cookGesturesOnly(self):
		for i in range(len(self.TapeObject['Clips'])):
			CurrentClip = self.TapeObject['Clips'][i]
			## check for motionclip ##
			if CurrentClip['__class'] == "MotionClip":
				if CurrentClip['MoveType'] == 1:
					self.Clips.append(CurrentClip)
			elif CurrentClip['__class'] == "PictogramClip":
				self.Clips.append(CurrentClip)
			elif CurrentClip['__class'] == "GoldEffectClip":
				self.Clips.append(CurrentClip)
		self.TapeObject['Clips'] = self.Clips
	def cookControllerOnly(self):
		for i in range(len(self.TapeObject['Clips'])):
			CurrentClip = self.TapeObject['Clips'][i]
			## check for motionclip ##
			if CurrentClip['__class'] == "MotionClip":
				if CurrentClip['MoveType'] == 0:
					self.Clips.append(CurrentClip)
			elif CurrentClip['__class'] == "PictogramClip":
				self.Clips.append(CurrentClip)
			elif CurrentClip['__class'] == "GoldEffectClip":
				self.Clips.append(CurrentClip)
		self.TapeObject['Clips'] = self.Clips
	def cookPlatform(self,platform,fileHandle):
		if platform == "NX" or platform == "WII" or platform == "WIIU" or platform == "PC":
			self.cookControllerOnly()
			fileHandle.write(json.dumps(self.TapeObject,separators=(',', ':')))
		elif platform == "ORBIS" or platform == "DURANGO":
			fileHandle.write(json.dumps(self.TapeObject,separators=(',', ':')))
		elif platform == "X360":
			self.cookGesturesOnly()
			fileHandle.write(json.dumps(self.TapeObject,separators=(',', ':')))
		fileHandle.close()
def cookToPlatform(dtape,output,platform):
	outFile = open(output,'w')
	dtapeObject = Tape(dtape)
	dtapeObject.cookPlatform(platform,outFile)
