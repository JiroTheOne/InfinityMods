# Disney Infinity .oct .bent .banm .mer reader
# Author: zzh8829
# Email: zzh8829#gmail.com
import os
import io
import pprint
import sys
import struct

types = {
	'int8_t': 'b',
	'uint8_t': 'B',
	'int16_t': 'h',
	'uint16_t': 'H',
	'int32_t': 'i',
	'uint32_t': 'I',
	'int64_t': 'q',
	'uint64_t': 'Q',
	'float': 'f',
	'double': 'd',
	'char': 'c',
    'bool': '?',
    'pad': 'x',
    'void*': 'P',
}

class BStream:
	def __init__(self, **kwargs):
		if "file" in kwargs:
			self.stream = open(kwargs["file"], "rb")
		elif "stream" in kwargs:
			self.stream = kwargs["stream"]
		elif "bytes" in kwargs:
			self.stream = io.BytesIO(kwargs["bytes"])
		else:
			raise Exception("UnityStream arguments error")

	def read(self, type_name='char'):
		if isinstance(type_name,int):
			return self.unpack('%ds'%type_name)[0]
		fmt = types[type_name.lower()]
		return self.unpack(fmt)[0]

	def unpack(self, fmt):
		return struct.unpack(fmt, self.stream.read(struct.calcsize(fmt)))

	def read_cstring(self):
		string = ""
		while True:
			char = self.read('char')
			if ord(char) == 0:
				break
			string += char.decode("utf-8")
		return string

	def read_string(self):
		return self.unpack('%ds'%self.read('uint32_t'))[0].decode('utf-8')

	def read_all(self):
		return self.read(self.size() - self.get_position())

	def read_int12(self):
		return int.from_bytes(self.read(3),byteorder="little")

	def get_position(self):
		return self.stream.tell()

	def set_position(self, pos, whence=0):
		self.stream.seek(pos, whence)

	def size(self):
		pos = self.get_position()
		self.set_position(0,2)
		end = self.get_position()
		self.set_position(pos,0)
		return end

	def align(self, alignment=4):
		self.set_position((self.get_position() + alignment - 1) // alignment * alignment) 


def read_oct(stream):
	file_size = stream.size()

	magic = stream.read(12)
	header = stream.read(10)
	padding = stream.read(39)
	strings = [""]

	s = ""
	while s!="\x01":
		s = stream.read_cstring()
		strings.append(s)

	padding = stream.read(2)

	while stream.get_position() != file_size:
		flag = stream.read("uint16_t")
		name = strings[stream.read("uint16_t")]

		indent,format = divmod(flag,0x400)

		print("\t"*(indent-1) + name + "[%04x]"%format, end=" = ")

		# unknown sign all treat as unsigned !!!

		if format == 0x01: 
			print()
		elif format == 0x05: 
			data = strings[stream.read("uint16_t")]
			print("'%s'"%data)
		elif format == 0x0A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(strings[stream.read("uint16_t")])
			print(data)
		elif format == 0x0B:
			data = strings[stream.read("uint16_t")]
			print("'%s'"%data)
		elif format == 0x12:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("float"))
			print(data)
		elif format == 0x13:
			data = stream.read("float")
			print(data)
		elif format == 0x1A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("int8_t"))
			print(data)
		elif format == 0x1B:
			data = stream.read("int8_t")
			print(data)
		elif format == 0x23:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x4A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(strings[stream.read("uint16_t")])
			print(data)
		elif format == 0x5A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x63: # binary data
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint8_t"))
			print(data)
		elif format == 0x11A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint16_t"))
			print(data)
		elif format == 0x11B:
			data = stream.read("uint16_t")
			print(data)
		elif format == 0x15A:
			count = stream.read("uint16_t")
			data = []
			for i in range(count):
				data.append(stream.read("uint16_t"))
			print(data)
		elif format == 0x21A:
			count = stream.read("uint8_t")
			data = []
			for i in range(count):
				data.append(stream.read_int12())
			print(data)	
		elif format == 0x21B:
			data = stream.read_int12()
			print(data)
		elif format == 0x31B:
			data = stream.read("uint32_t")
			print(data)
		else:
			print("unknown format: %x offset: %x"%(flag,stream.get_position()))
			sys.stderr.write("unknown format: %x offset: %x\n"%(flag,stream.get_position()))
			print(stream.read_all()[:100])
			break

if __name__ == '__main__':
	filename = sys.argv[1]
	read_oct(BStream(file=filename))

