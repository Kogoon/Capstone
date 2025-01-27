import os
import kernel
import kavutil

from sklearn.externals import joblib
import csv,os,pefile
import yara
import math
import hashlib
import csv
import numpy as np

import warnings
warnings.filterwarnings("ignore")

class PE_features():

	IMAGE_DOS_HEADER = [
						"e_cblp",\
						"e_cp", \
						"e_cparhdr",\
						"e_maxalloc",\
						"e_sp",\
						"e_lfanew"]

	FILE_HEADER= ["NumberOfSections","CreationYear"] + [ "FH_char" + str(i) for i in range(15)]
				

	OPTIONAL_HEADER1 = [
						"MajorLinkerVersion",\
						"MinorLinkerVersion",\
						"SizeOfCode",\
						"SizeOfializedData",\
						"SizeOfUninitializedData",\
						"AddressOfEntryPoint",\
						"BaseOfCode",\
						"BaseOfData",\
						"ImageBase",\
						"SectionAlignment",\
						"FileAlignment",\
						"MajorOperatingSystemVersion",\
						"MinorOperatingSystemVersion",\
						"MajorImageVersion",\
						"MinorImageVersion",\
						"MajorSubsystemVersion",\
						"MinorSubsystemVersion",\
						"SizeOfImage",\
						"SizeOfHeaders",\
						"CheckSum",\
						"Subsystem"] 
	OPTIONAL_HEADER_DLL_char = [ "OH_DLLchar" + str(i) for i in range(11)]				   
							
	OPTIONAL_HEADER2 = [
						"SizeOfStackReserve",\
						"SizeOfStackCommit",\
						"SizeOfHeapReserve",\
						"SizeOfHeapCommit",\
						"LoaderFlags"]  # boolean check for zero or not
	OPTIONAL_HEADER = OPTIONAL_HEADER1 + OPTIONAL_HEADER_DLL_char + OPTIONAL_HEADER2
	Derived_header = ["sus_sections","non_sus_sections", "packer","packer_type","E_text","E_data","filesize","E_file","fileinfo"]
	
	def __init__(self, source, path):
		self.source = source
		yara_path = path + "/peid.yara"
		self.rules= yara.compile(filepath=yara_path)
		
	def file_creation_year(self,seconds):
		tmp = 1970 + ((int(seconds) / 86400) / 365)
		return int(tmp in range (1980,2016)) 

	def FILE_HEADER_Char_boolean_set(self,pe):
		tmp = [pe.FILE_HEADER.IMAGE_FILE_RELOCS_STRIPPED,\
			pe.FILE_HEADER.IMAGE_FILE_EXECUTABLE_IMAGE,\
			pe.FILE_HEADER.IMAGE_FILE_LINE_NUMS_STRIPPED,\
			pe.FILE_HEADER.IMAGE_FILE_LOCAL_SYMS_STRIPPED,\
			pe.FILE_HEADER.IMAGE_FILE_AGGRESIVE_WS_TRIM,\
			pe.FILE_HEADER.IMAGE_FILE_LARGE_ADDRESS_AWARE,\
			pe.FILE_HEADER.IMAGE_FILE_BYTES_REVERSED_LO,\
			pe.FILE_HEADER.IMAGE_FILE_32BIT_MACHINE,\
			pe.FILE_HEADER.IMAGE_FILE_DEBUG_STRIPPED,\
			pe.FILE_HEADER.IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP,\
			pe.FILE_HEADER.IMAGE_FILE_NET_RUN_FROM_SWAP,\
			pe.FILE_HEADER.IMAGE_FILE_SYSTEM,\
			pe.FILE_HEADER.IMAGE_FILE_DLL,\
			pe.FILE_HEADER.IMAGE_FILE_UP_SYSTEM_ONLY,\
			pe.FILE_HEADER.IMAGE_FILE_BYTES_REVERSED_HI
			]
		return [int(s) for s in tmp]

	def OPTIONAL_HEADER_DLLChar(self,pe):
		tmp = [
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NX_COMPAT ,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_ISOLATION,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_SEH,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_BIND,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_WDM_DRIVER,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_APPCONTAINER,\
			pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_GUARD_CF
			]
		return [int(s) for s in tmp]

	def Optional_header_ImageBase(self,ImageBase):
		result= 0
		if ImageBase % (64 * 1024) == 0 and ImageBase in [268435456,65536,4194304]:
			result = 1
		return result

	def Optional_header_SectionAlignment(self,SectionAlignment,FileAlignment):
		"""This is boolean function and will return 0 or 1 based on condidtions
		that it SectionAlignment must be greater than or equal to FileAlignment
		"""
		return int(SectionAlignment >= FileAlignment)

	def Optional_header_FileAlignment(self,SectionAlignment,FileAlignment):
		result =0
		if SectionAlignment >= 512:
			if FileAlignment % 2 == 0 and FileAlignment in range(512,65537):
				result =1
		else: 
			if FileAlignment == SectionAlignment:
				result = 1
		return result

	def Optional_header_SizeOfImage(self,SizeOfImage,SectionAlignment):

		return int(SizeOfImage % SectionAlignment == 0)

	def Optional_header_SizeOfHeaders(self,SizeOfHeaders,FileAlignment):

		return int(SizeOfHeaders % FileAlignment == 0 )

	def extract_dos_header(self,pe):
		IMAGE_DOS_HEADER_data = [ 0 for i in range(6)]
		try:
			IMAGE_DOS_HEADER_data = [
								pe.DOS_HEADER.e_cblp,\
								pe.DOS_HEADER.e_cp, \
								pe.DOS_HEADER.e_cparhdr,\
								pe.DOS_HEADER.e_maxalloc,\
								pe.DOS_HEADER.e_sp,\
								pe.DOS_HEADER.e_lfanew]
		except Exception, e:
			print e
		return IMAGE_DOS_HEADER_data

	def extract_file_header(self,pe):   
		FILE_HEADER_data = [ 0 for i in range(3)]
		FILE_HEADER_char =  []
		try:
			FILE_HEADER_data = [ 
					pe.FILE_HEADER.NumberOfSections, \
					self.file_creation_year(pe.FILE_HEADER.TimeDateStamp)]
			FILE_HEADER_char = self.FILE_HEADER_Char_boolean_set(pe)
		except Exception, e:
			print e
		return FILE_HEADER_data + FILE_HEADER_char

	def extract_optional_header(self,pe):
		OPTIONAL_HEADER_data = [ 0 for i in range(21)]
		DLL_char =[]
		OPTIONAL_HEADER_data2 = [ 0 for i in range(6)]

		try:
			OPTIONAL_HEADER_data = [
				pe.OPTIONAL_HEADER.MajorLinkerVersion,\
				pe.OPTIONAL_HEADER.MinorLinkerVersion,\
				pe.OPTIONAL_HEADER.SizeOfCode,\
				pe.OPTIONAL_HEADER.SizeOfInitializedData,\
				pe.OPTIONAL_HEADER.SizeOfUninitializedData,\
				pe.OPTIONAL_HEADER.AddressOfEntryPoint,\
				pe.OPTIONAL_HEADER.BaseOfCode,\
				pe.OPTIONAL_HEADER.BaseOfData,\
				#Check the ImageBase for the condition
				self.Optional_header_ImageBase(pe.OPTIONAL_HEADER.ImageBase),\
				# Checking for SectionAlignment condition
				self.Optional_header_SectionAlignment(pe.OPTIONAL_HEADER.SectionAlignment,pe.OPTIONAL_HEADER.FileAlignment),\
				#Checking for FileAlignment condition
				self.Optional_header_FileAlignment(pe.OPTIONAL_HEADER.SectionAlignment,pe.OPTIONAL_HEADER.FileAlignment),\
				pe.OPTIONAL_HEADER.MajorOperatingSystemVersion,\
				pe.OPTIONAL_HEADER.MinorOperatingSystemVersion,\
				pe.OPTIONAL_HEADER.MajorImageVersion,\
				pe.OPTIONAL_HEADER.MinorImageVersion,\
				pe.OPTIONAL_HEADER.MajorSubsystemVersion,\
				pe.OPTIONAL_HEADER.MinorSubsystemVersion,\
				#Checking size of Image
				self.Optional_header_SizeOfImage(pe.OPTIONAL_HEADER.SizeOfImage,pe.OPTIONAL_HEADER.SectionAlignment),\
				#Checking for size of headers
				self.Optional_header_SizeOfHeaders(pe.OPTIONAL_HEADER.SizeOfHeaders,pe.OPTIONAL_HEADER.FileAlignment),\
				pe.OPTIONAL_HEADER.CheckSum,\
				pe.OPTIONAL_HEADER.Subsystem]

			DLL_char = self.OPTIONAL_HEADER_DLLChar(pe)

			OPTIONAL_HEADER_data2= [				
				pe.OPTIONAL_HEADER.SizeOfStackReserve,\
				pe.OPTIONAL_HEADER.SizeOfStackCommit,\
				pe.OPTIONAL_HEADER.SizeOfHeapReserve,\
				pe.OPTIONAL_HEADER.SizeOfHeapCommit,\
				int(pe.OPTIONAL_HEADER.LoaderFlags == 0) ]
		except Exception, e:
			print e
		return OPTIONAL_HEADER_data + DLL_char + OPTIONAL_HEADER_data2

	def get_count_suspicious_sections(self,pe):
		result=[]
		tmp =[]
		benign_sections = set(['.text','.data','.rdata','.idata','.edata','.rsrc','.bss','.crt','.tls'])
		for section in pe.sections:
			tmp.append(section.Name.split('\x00')[0])
		non_sus_sections = len(set(tmp).intersection(benign_sections))
		result=[len(tmp) - non_sus_sections, non_sus_sections]
		return result

	def check_packer(self,filepath):

		result=[]
		matches = self.rules.match(filepath)

		try:
			if matches == [] or matches == {}:
				result.append([0,"NoPacker"])
			else:
				result.append([1,matches['main'][0]['rule']])
		except:
			result.append([1,matches[0]])

		return result

	def get_text_data_entropy(self,pe):
		result=[0.0,0.0]
		for section in pe.sections:
			s_name = section.Name.split('\x00')[0]
			if s_name == ".text":
				result[0]= section.get_entropy()
			elif s_name == ".data":
				result[1]= section.get_entropy()
			else:
				pass
		return result  

	def get_file_bytes_size(self,filepath):
		f = open(filepath, "rb")
		byteArr = map(ord, f.read())
		f.close()
		fileSize = len(byteArr)
		return byteArr,fileSize

	def cal_byteFrequency(self,byteArr,fileSize):
		freqList = []
		for b in range(256):
			ctr = 0
			for byte in byteArr:
				if byte == b:
					ctr += 1
			freqList.append(float(ctr) / fileSize)
		return freqList

	def get_file_entropy(self,filepath):
		byteArr, fileSize = self.get_file_bytes_size(filepath)
		freqList = self.cal_byteFrequency(byteArr,fileSize)
		# Shannon entropy
		ent = 0.0
		for freq in freqList:
			if freq > 0:
				ent +=  - freq * math.log(freq, 2)

			#ent = -ent
		return [fileSize,ent]

	def get_fileinfo(self,pe):
		result=[]
		try:
			FileVersion	= pe.FileInfo[0].StringTable[0].entries['FileVersion']
			ProductVersion = pe.FileInfo[0].StringTable[0].entries['ProductVersion']
			ProductName =	pe.FileInfo[0].StringTable[0].entries['ProductName']
			CompanyName = pe.FileInfo[0].StringTable[0].entries['CompanyName']
		#getting Lower and 
			FileVersionLS	= pe.VS_FIXEDFILEINFO.FileVersionLS
			FileVersionMS	= pe.VS_FIXEDFILEINFO.FileVersionMS
			ProductVersionLS = pe.VS_FIXEDFILEINFO.ProductVersionLS
			ProductVersionMS = pe.VS_FIXEDFILEINFO.ProductVersionMS
		except Exception, e:
			result=["error"]
		#print "{} while opening {}".format(e,filepath)
		else:
		#shifting byte
			FileVersion = (FileVersionMS >> 16, FileVersionMS & 0xFFFF, FileVersionLS >> 16, FileVersionLS & 0xFFFF)
			ProductVersion = (ProductVersionMS >> 16, ProductVersionMS & 0xFFFF, ProductVersionLS >> 16, ProductVersionLS & 0xFFFF)
			result = [FileVersion,ProductVersion,ProductName,CompanyName]
		return int ( result[0] != 'error')


	def extract_all(self):
		data =[]
		filepath = self.source
		try:
			pe = pefile.PE(filepath)
		except Exception, e:
			print "{} while opening {}".format(e,filepath)
		else:
			data += self.extract_dos_header(pe)
			data += self.extract_file_header(pe)
			data += self.extract_optional_header(pe)
			num_ss_nss = self.get_count_suspicious_sections(pe)
			data += num_ss_nss
			packer = self.check_packer(filepath)
			data += packer[0]
			entropy_sections = self.get_text_data_entropy(pe)
			data += entropy_sections
			f_size_entropy = self.get_file_entropy(filepath)
			data += f_size_entropy
			fileinfo = self.get_fileinfo(pe)
			data.append(fileinfo)
			magic = pe.OPTIONAL_HEADER.Magic
		
		return data, magic

class KavMain:
	# -------------------------------------------------------------------------
	# init(self, model_path)
	# 플러그인 엔진을 초기화한다.
	# 입력값 : model_path - 모델 파일 경로
	# 리턴값 : 0 - 성공, 0 이외의 값 - 실패
	# -------------------------------------------------------------------------
	def init(self, plugins_path, verbose=False):
		# 악성코드 탐지 모델 등록
		path = plugins_path + "/model.joblib"
		self.ml_model = joblib.load(path)
		self.plugins_path = plugins_path

		return 0

	# ---------------------------------------------------------------------
	# uninit(self)
	# 플러그인 엔진을 종료한다.
	# 리턴값 : 0 - 성공, 0 이외의 값 - 실패
	# ---------------------------------------------------------------------
	def uninit(self):
		del self.ml_model
		del self.plugins_path

		return 0

	# ---------------------------------------------------------------------
	# scan(self, filehandle, filename)
	# 악성코드의 악성 정도를 검사한다.
	# 인력값 : filehandle - 파일 핸들
	#		  filename - 파일 이름
	#		   fileformat - 파일 포맷
	# 리턴값 : 악성코드 발견 여부, 악성코드 점수
	# ---------------------------------------------------------------------
	def scan(self, filehandle, filename, fileformat, filename_ex):
		path = self.plugins_path
		try:
			if 'ff_pe' in fileformat:
				ret = self.__scan_ml(filehandle, filename, fileformat, path)
				return ret
		except IOError:
			pass

		return False, '', -1, kernel.NOT_FOUND

	# ---------------------------------------------------------------------
	# PE 정보로 악성코드 여부를 탐지한다.
	# ---------------------------------------------------------------------
	def __scan_ml(self, filehandle, filename, fileformat, path):
		clf = self.ml_model
		ft = PE_features(filename, path)
		data, magic = ft.extract_all()

		if magic != 267 or len(data) != 69:
			return False, '', -1, kernel.NOT_FOUND

		pattern_path = path + "/patterns.csv"
		f = open(pattern_path, 'r')
		rd = csv.reader(f)
		for row in rd:
			patterns = row

		packer_type = [0] * len(patterns)

		try:
			idx = patterns.index(data[63])
		except ValueError:
			idx = 10

		packer_type[idx] = 1
		del data[63]
		data = data + packer_type
		data = np.asarray(data).reshape((1, -1))
		rns = clf.predict_proba(data)[0][1]
		print rns
		pat = "ML Confidence - " + str(rns) 

		print pat

		if rns > 0.8:
			return True, pat, 0, kernel.INFECTED
		else:
			return False, '', -1, kernel.NOT_FOUND


	# ---------------------------------------------------------------------
	# disinfect(self, filename, malware_id)
	# 악성코드를 치료한다.
	# 인력값 : filename - 파일 이름
	#		  malware_id - 치료할 악성코드 ID
	# 리턴값 : 발견한 악성코드 이름
	# ---------------------------------------------------------------------
	def disinfect(self):
		try:
			if malware_id == 0: # 삭제를 통해 치료를 하는 코드 
				os.remove(filename) # 파일 삭제
				return True # 치료 완료 리턴
		except IOError:
			pass

		return False # 치료 실패 리턴

	# 플러그인 엔진이 진단/치료 가능한 악성코드의 리스트를 알려준다.
	def viruslist(self):
		vlists = []
		return vlists

	# 플러그인 엔진의 주요 정보를 알려준다.
	def getinfo(self):
		info = dict()

		info['author'] = ''
		info['version'] = '1.0'
		info['title'] = 'ML Detection Engine'
		info['kmd_name'] = 'ML'

		return info
