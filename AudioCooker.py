import os
from ubisoftcrc import crc32
import wave
import sys
from io import BytesIO
import struct
import importlib
import shutil
from platform import python_version
if python_version()[0] != "3":
	print("PYTHON MUST BE VERSION 3")
	quit()
vgAudio = r"F:\JDHits_MASTER\TOOLS\Bin\VGAudioCli.exe"
DSPADPCM = r"F:\JDHits_MASTER\TOOLS\Bin\dspadpcm.exe"
opusEncoder = r"F:\JDHits_MASTER\TOOLS\Bin\OpusEncoder.exe"
sox = r"F:\JDHits_MASTER\TOOLS\Bin\sox\sox.exe"
def getPlatform(platform):
	enginePlat_TO_rakiPlat = {
		"PC":    b"Win ",
		"WIIU":  b"Cafe",
		"NX" :   b"Nx  ",
		"WII":   b"Wii ",
		"ORBIS": b"Orbi"
	}
	return enginePlat_TO_rakiPlat[platform]
class RAKI_BinWaveData:
	def __init__(self,platform,format,audioFile,outputAudio,interleave=True):
		self.RAKI = b"RAKI"
		self.version = crc32("planedec50")
		self.platform = getPlatform(platform)
		self.format = format
		self.nonDataSize = 0 # go back and write to this when were done with the header!
		self.dataOffset = 0 # go back and write...
		self.nbChunks = 0 # depends on format
		self.binFlags = 0 # what is this???
		self.chunks = []
		self.inputAudio = audioFile
		self.tmpAudio = "C:/temp/temp.wav"
		self.output = open(outputAudio,'wb')
		self.interleave = interleave
	def getEndianessFromPlatform(self):
		global CSerializerObject
		if self.platform == b"Win " or self.platform == b"Nx  " or self.platform == b"Orbi":
			module = importlib.import_module('CSerializerObject')
			myclass = getattr(module,'CSerializerObject_LE')
			CSerializerObject = myclass
		else:
			module = importlib.import_module('CSerializerObject')
			myclass = getattr(module,'CSerializerObject')
			CSerializerObject = myclass
	def serializeRAKIHeader(self):
		self.HeaderObject = BytesIO()
		CSerializerObject.rawBytes(self.HeaderObject,self.RAKI)
		CSerializerObject.uint32(self.HeaderObject,self.version)
		CSerializerObject.rawBytes(self.HeaderObject,self.platform)
		CSerializerObject.rawBytes(self.HeaderObject,self.format)
		CSerializerObject.uint32(self.HeaderObject,self.nonDataSize)
		CSerializerObject.uint32(self.HeaderObject,self.dataOffset)
		CSerializerObject.uint32(self.HeaderObject,self.nbChunks)
		CSerializerObject.uint32(self.HeaderObject,self.binFlags)
	def serializeChunkHeaders(self):
		self.ChunkHeaderData = BytesIO()
		for i in range(len(self.chunks)):
			CSerializerObject.rawBytes(self.ChunkHeaderData,self.chunks[i]['signature'])
			CSerializerObject.uint32(self.ChunkHeaderData,self.chunks[i]['chunkOffset'])
			CSerializerObject.uint32(self.ChunkHeaderData,self.chunks[i]['chunkSize'])
	def serializeChunkData(self):
		self.ChunkData = BytesIO()
		for i in range(len(self.chunks)):
			for dataField in self.chunks[i]['chunkdata']:
				CSerializerObject.manual(self.ChunkData,self.chunks[i]['chunkdata'][dataField][0],self.chunks[i]['chunkdata'][dataField][1])
	def serializeRAKI(self):
		self.serializeRAKIHeader()
		self.serializeChunkHeaders()
		self.serializeChunkData()
	def writeRAKI(self):
		self.output.write(self.HeaderObject.getvalue())
		self.output.write(self.ChunkHeaderData.getvalue())
		self.output.write(self.ChunkData.getvalue())
	def pcmCook(self):
		self.getEndianessFromPlatform()
		## load and set the wav file ##
		OrigAudio = wave.open(self.inputAudio)
		frequency = OrigAudio.getframerate()
		channels = OrigAudio.getnchannels()
		fmt = {
			"signature": b"fmt ",
			"chunkOffset": 0x38, # hard coded
			"chunkSize": 0x12, # hard coded
			"chunkdata": {
				"audioFormat": (1,'H'), # PCM
				"channels": (OrigAudio.getnchannels(),'H'),
				"frequency": (OrigAudio.getframerate(),'I'),
				"byterate": (int(frequency * channels * 16/8),'I'),
				"blockalign": (int(channels * 16/8),'H'),
				"bitspersample": (16,'I')
			}
		}
		data = {
			"signature": b"data",
			'chunkOffset': 0x4a, # hard coded
			'chunkSize': OrigAudio.getnframes()*4, ## is this really just blockalign * nframes?
			'chunkdata': {
				'rawAudioData': (OrigAudio.readframes(OrigAudio.getnframes()),'raw')
			}
		}
		## change header data ##
		self.format = b"pcm "
		self.nbChunks = 2
		self.nonDataSize = 0x4a
		self.dataOffset = 0x4a
		self.chunks.append(fmt)
		self.chunks.append(data)
		## serialize EVERYTHING ##
		self.serializeRAKI()
		## write the data to the outputFile ##
		self.writeRAKI()
		## close the output file ##
		self.output.close()
		OrigAudio.close()
	def IDSPCook(self):
		encoder = vgAudio
		IDSP = r"C:/temp/temp.idsp"
		os.system("{} -c -i {} -o {}".format(encoder,self.tmpAudio,IDSP))
		with open(IDSP,'rb') as fileHandle:
			fileHandle.seek(8,0)
			IDSPData = {
				"ChannelCount": struct.unpack('>I',fileHandle.read(0x4))[0],
				"SampleRate": struct.unpack('>I',fileHandle.read(0x4))[0],
				"SampleCount": struct.unpack('>I',fileHandle.read(0x4))[0],
				"LoopStart": struct.unpack('>I',fileHandle.read(0x4))[0],
				"LoopEnd": struct.unpack('>I',fileHandle.read(0x4))[0],
				"BlockSize": struct.unpack('>I',fileHandle.read(0x4))[0],
				"StreamInfoSize": struct.unpack('>I',fileHandle.read(0x4))[0],
				"ChannelInfoSize": struct.unpack('>I',fileHandle.read(0x4))[0],
				"HeaderSize": struct.unpack('>I',fileHandle.read(0x4))[0],
				"AudioDataSize": struct.unpack('>I',fileHandle.read(0x4))[0], ## FOR ONE CHANNEL ONLY ##
				"DUMMY": fileHandle.read(0x10),
				"dspL": fileHandle.read(0x60),
				"dspR": fileHandle.read(0x60),
				"datS": fileHandle.read()
			}
			del IDSPData['DUMMY']
		return IDSPData
	def StereoDSPCook(self):
		encoder = DSPADPCM
		DSP_L = r"C:/temp/temp_L.dsp"
		DSP_R = r"C:/temp/temp_R.dsp"
		os.system("{} -e {} -l0-{} {}".format(encoder,self.tmpAudioL,self.SampleCount-1,DSP_L))
		os.system("{} -e {} -l0-{} {}".format(encoder,self.tmpAudioR,self.SampleCount-1,DSP_R))
		with open(DSP_L,'rb') as DSPL, open(DSP_R,'rb') as DSPR:
			DSPData = {
				"LeftData": {
					"dspL": DSPL.read(0x60),
					"datL": DSPL.read(),
					"size": DSPL.tell() - 0x60
				},
				"RightData": {
					"dspR": DSPR.read(0x60),
					"dummy": DSPR.seek(0x8,1),
					"datR": DSPR.read(),
					"size": DSPR.tell() - 0x60
				}
			}
		return DSPData
	def MonoDSPCook(self):
		encoder = vgAudio
		DSP_L = r"C:/temp/temp_L.dsp"
		os.system("{} -c -i {} -o {}".format(encoder,self.tmpAudioL,DSP_L))
		with open(DSP_L,'rb') as DSPL:
			DSPData = {
				'LeftData': {
					'dspL': DSPL.read(0x60),
					'datL': DSPL.read(),
					'size': DSPL.tell() - 0x60
				}
			}
		return DSPData
	def adpcCook(self):
		OrigAudio = wave.open(self.inputAudio)
		self.getEndianessFromPlatform()
		## encode to 32000HZ ##
		if os.path.isdir('C:\\temp\\') == False:
			os.mkdir('C:\\temp\\')
		encoder = sox
		## encode into intermediate format ##
		if self.interleave:
			os.system("{} {} -r 32000 {}".format(encoder,self.inputAudio,self.tmpAudio))
			self.ADPC_TYPE = "datS"
			self.IDSPRaw = self.IDSPCook() ## returns idsp data ##
		else:
			if OrigAudio.getnchannels() == 2:
				self.ADPC_TYPE = "datR"
				self.tmpAudioL = "C:/temp/temp_L.wav"
				self.tmpAudioR = "C:/temp/temp_R.wav"
				os.system("{} {} -r 32000 {} remix 1".format(encoder,self.inputAudio,self.tmpAudioL))
				os.system("{} {} -r 32000 {} remix 2".format(encoder,self.inputAudio,self.tmpAudioR))
				newAud = wave.open(self.tmpAudioL)
				self.SampleCount = newAud.getnframes()
				newAud.close()
				self.SDSPRaw = self.StereoDSPCook()
			elif OrigAudio.getnchannels() == 1:
				self.ADPC_TYPE = "datL"
				self.tmpAudioL = "C:/temp/temp_L.wav"
				os.system("{} {} -r 32000 {}".format(encoder,self.inputAudio,self.tmpAudioL))
				self.DSPRaw = self.MonoDSPCook()
		## load and set the audio parameters ##
		frequency = OrigAudio.getframerate()
		channels = OrigAudio.getnchannels()
		fmt = {
			'signature': b"fmt ",
			'chunkOffset': 0x50, # hard coded
			'chunkSize': 0x12, # hard coded
			'chunkdata': {
				'audioFormat': (2,'H'), # ADPC
				'channels': (OrigAudio.getnchannels(),'H'),
				'frequency': (32000,'I'),
				'byterate': (int(frequency * channels * 16/16),'I'),
				'blockalign': (int(channels * 16/16),'H'),
				'bitspersample': (16,'H'),
				'padding': (0,'H')
			}
		}
		
		if self.ADPC_TYPE == "datS":
			## CASE OF IDSP FILE ##
			IDSPData = self.IDSPRaw
			dspL = {
				'signature': b"dspL",
				'chunkOffset': 0x62,
				'chunkSize': 0x60,
				'chunkdata': {
					'rawdata': (IDSPData['dspL'],'raw')
				}
			}
			dspR = {
				'signature': b"dspR",
				'chunkOffset': 0xC2,
				'chunkSize': 0x60,
				'chunkdata': {
					'rawdata': (IDSPData['dspR'],'raw'),
					'PADDING': (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00','raw')
				}
			}
			datS = {
				'signature': b"datS",
				'chunkOffset': 0x140,
				'chunkSize': int(IDSPData['AudioDataSize'] * 2),
				'chunkdata': {
					'rawdata': (IDSPData['datS'],'raw')
				}
			}
			self.chunks.append(fmt)
			self.chunks.append(dspL)
			self.chunks.append(dspR)
			self.chunks.append(datS)
			self.nonDataSize = 0x122
			self.dataOffset = 0x140
		elif self.ADPC_TYPE == "datR":
			## CASE OF UNINTERLEAVE ##
			DSPData = self.SDSPRaw
			fmt['chunkOffset'] = 0x5C
			dspL = {
				'signature': b"dspL",
				'chunkOffset': 0x6E,
				'chunkSize': 0x60,
				'chunkdata': {
					'rawdata': (DSPData['LeftData']['dspL'],'raw')
				}
			}
			dspR = {
				'signature': b"dspR",
				'chunkOffset': 0xCE,
				'chunkSize': 0x60,
				'chunkdata': {
					'rawdata': (DSPData['RightData']['dspR'],'raw'),
					'PADDING': (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00','raw')
				}
			}
			datL = {
				'signature': b"datL",
				'chunkOffset': 0x140,
				'chunkSize': DSPData['LeftData']['size'],
				'chunkdata': {
					'rawdata': (DSPData['LeftData']['datL'],'raw'),
					'PADDING': (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00','raw')
				}
			}
			datR = {
				'signature': b"datR",
				'chunkOffset': 0x140 + DSPData['LeftData']['size'] + 0x10, ## so it comes AFTER the datL chunk
				'chunkSize': DSPData['RightData']['size'],
				'chunkdata': {
					'rawdata': (DSPData['RightData']['datR'],'raw'),
					'PADDING': (b'\x00\x00\x00\x00\x00\x00\x00\x00','raw')
				}
			}
			self.chunks.append(fmt)
			self.chunks.append(dspL)
			self.chunks.append(dspR)
			self.chunks.append(datL)
			self.chunks.append(datR)
			self.nonDataSize = 0x12E
			self.dataOffset = 0x140
		elif self.ADPC_TYPE == "datL":
			## MONO AUDIO ##
			DSPData = self.DSPRaw
			fmt['chunkOffset'] = 0x44
			dspL = {
				'signature': b"dspL",
				'chunkOffset': 0x56,
				'chunkSize': 0x60,
				'chunkdata': {
					'rawdata': (DSPData['LeftData']['dspL'],'raw'),
					'padding': (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00','raw')
				}
			}
			datL = {
				'signature': b"datL",
				'chunkOffset': 0xC0,
				'chunkSize': DSPData['LeftData']['size'],
				'chunkdata': {
					'rawdata': (DSPData['LeftData']['datL'],'raw')
				}
			}
			self.chunks.append(fmt)
			self.chunks.append(dspL)
			self.chunks.append(datL)
			self.nonDataSize = 0xB6
			self.dataOffset = 0xC0
		## change header data ##
		self.format = b"adpc"
		self.nbChunks = len(self.chunks)
		
		
		
		## serialize EVERYTHING ##
		self.serializeRAKI()
		## write the data to the outputFile ##
		self.writeRAKI()
		## close the output file and clean up temp ##
		self.output.close()
		OrigAudio.close()
		input("")
		shutil.rmtree('C:/temp')
	def getSampleCount(self,byteAmount,channels,bits_per_sample=16):
		return int((byteAmount * 8) / channels / bits_per_sample)
	def nxCook(self):
		## load and set the wav file ##
		self.getEndianessFromPlatform()
		OrigAudio = wave.open(self.inputAudio)
		frequency = OrigAudio.getframerate()
		channels = OrigAudio.getnchannels()
		if os.path.isdir('C:\\temp\\') == False:
			os.mkdir('C:\\temp\\')
		## encode into intermediate file ##
		encoder = opusEncoder
		os.system("{} --bitrate 192000 -o {} {}".format(encoder,self.tmpAudio,self.inputAudio))
		with open(self.tmpAudio,'rb') as fileHandle:
			self.rawData = fileHandle.read()
			self.rawDataSize = fileHandle.tell()
		## get audio data ##
		fmt = {
			'signature': b"fmt ",
			'chunkOffset': 0x44, # hard coded
			'chunkSize': 0x10, # hard coded
			'chunkdata': {
				'audioFormat': (0x63,'H'), # PCM
				'channels': (OrigAudio.getnchannels(),'H'),
				'frequency': (OrigAudio.getframerate(),'I'),
				'byterate': (int(frequency * channels * 16/8),'I'),
				'blockalign': (int(channels * 16/8),'H'),
				'bitspersample': (16,'H') ## why was this changed to a short ??? ##
			}
		}
		AdIn = {
			'signature': b"AdIn",
			'chunkOffset': 0x54, # hard coded
			'chunkSize': 0x4, # hard coded
			'chunkdata': {
				'sampleCount': (self.getSampleCount(OrigAudio.getnframes()*4,OrigAudio.getnchannels(),16),'I')
			}
		}
		data = {
			'signature': b"data",
			'chunkOffset': 0x58,
			'chunkSize': self.rawDataSize,
			'chunkdata': {
				'rawdata': (self.rawData,'raw')
			}
		}
		
		## change header data ##
		self.chunks.append(fmt)
		self.chunks.append(AdIn)
		self.chunks.append(data)
		self.format = b"Nx  "
		self.nbChunks = len(self.chunks)
		self.nonDataSize = 0x58
		self.dataOffset = 0x58
		
		## serialize EVERYTHING ##
		self.serializeRAKI()
		self.writeRAKI()
		## close the output file ##
		self.output.close()
		OrigAudio.close()
		shutil.rmtree('C:/temp')		
def convertToAudio(inputAudio,outputAudio,platform,format,interleave=True):
	audio = RAKI_BinWaveData(platform,format,inputAudio,outputAudio,interleave)
	## PCM for NX PC and ORBIS
	if (platform == "NX" or platform == "PC" or platform == "ORBIS") and format == "pcm ":
		audio.pcmCook()
	if (platform == "NX" and format == "Nx  "):
		audio.nxCook()
	if (platform == "WII" or platform == "WIIU") and format == "adpc":
		audio.adpcCook()
	del audio
def main():
	try:
		inputAudio = sys.argv[1]
		outputAudio = sys.argv[2]
		platform = sys.argv[3]
		format = sys.argv[4]
		try:
			interleave = sys.argv[5]
			if interleave == "False":
				interleave = False
			elif interleave == "True":
				interleave = True
		except:
			interleave = True
		audio = RAKI_BinWaveData(platform,format,inputAudio,outputAudio,interleave)
		## PCM for NX PC and ORBIS
		if (platform == "NX" or platform == "PC" or platform == "ORBIS") and format == "pcm ":
			audio.pcmCook()
		if (platform == "NX" and format == "Nx  "):
			audio.nxCook()
		if (platform == "WII" or platform == "WIIU") and format == "adpc":
			audio.adpcCook()
		del audio
	except IndexError:
		print("USAGE: ")
		print("AudioCooker.py inputAudio outputAudio platform format {interleave=True/False}")

if __name__ == "__main__":
	main()
