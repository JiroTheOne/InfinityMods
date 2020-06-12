#! python3
import os
import sys

# init
filename=sys.argv[1]
file_length_in_bytes = os.path.getsize(filename)


with open(filename, "rb") as binary_file:

    binary_file.seek(0, 0)

    header = binary_file.read(4)
    if header != b'\xcd\xab\x23\x01':
        raise Exception("Wrong header. Please ensure that the file is a valid chd file")
    print(filename + " Header:" + str(header.hex() ))

    offset = str(binary_file.tell())
    extendedHeader = binary_file.read(8)
    print("Extended Header:" + str(extendedHeader.hex()) + " Offset:" + offset )

    offset = str(binary_file.tell())
    fieldsSize = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Text fields block size (in bytes):" + str(fieldsSize) + " Offset:" + offset )

    offset = str(binary_file.tell())
    misteryNumber = int.from_bytes(binary_file.read(4), byteorder='little')
    print("misteryNumber:" + str(misteryNumber) +" "+ str(hex(misteryNumber)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    misteryNumber = int.from_bytes(binary_file.read(4), byteorder='little')
    print("misteryNumber2:" + str(misteryNumber) +" "+ str(hex(misteryNumber)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    misteryNumber = int.from_bytes(binary_file.read(4), byteorder='little')
    print("misteryNumber3:" + str(misteryNumber) +" "+ str(hex(misteryNumber)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    misteryNumber = int.from_bytes(binary_file.read(4), byteorder='little')
    print("misteryNumber4:" + str(misteryNumber) +" "+ str(hex(misteryNumber)) + " Offset:" + offset )

    print("Text fields START offset:" + str(binary_file.tell()))
    numberOfFields=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<fieldsStartOffset+fieldsSize:
        currentFieldSize=int.from_bytes(binary_file.read(2), byteorder='little')
        fieldName=binary_file.read(currentFieldSize+1)
        print("Size:" + str(currentFieldSize) + " String:" + str(fieldName))
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    print("Text fields END offset:" + str(binary_file.tell()))

    offset = str(binary_file.tell())
    misteryNumber = int.from_bytes(binary_file.read(3), byteorder='little')
    print("misteryNumber5:" + str(misteryNumber) +" "+ str(hex(misteryNumber)) + " Offset:" + offset )

    print("DataStructure START offset:" + str(binary_file.tell()))
    numberOfFields=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        currentOffset=binary_file.tell()
        currentFieldSize=int.from_bytes(binary_file.read(2), byteorder='little')
        if currentFieldSize==0:
            break
        fieldName=binary_file.read(currentFieldSize+1)
        print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " Hex:" + fieldName.hex() + " String:" + str(fieldName) )
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    binary_file.seek(binary_file.tell()-2, 0) # going back since we have read two bytes more DIRTY HACK
    print("DataStructure END offset:" + str(binary_file.tell()))

    offset = str(binary_file.tell())
    misterydata = binary_file.read(77)
    print("MisteryData:" + str(misterydata.hex()) + " Offset:" + offset )

    print("MisteryStructure (numbers are separated by 92) START offset:" + str(binary_file.tell())) # To implement 0xEDFE[length(short)][length*8bytes]
    numberOfFields=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        weirdDelimiter = binary_file.read(4)
        if weirdDelimiter!=b'\xff\xff\xff\xd0':
            # raise Exception("No delimiter found:" + str(weirdDelimiter))
            break
        currentOffset=binary_file.tell()
        weirdNumber=int.from_bytes(binary_file.read(4), byteorder='little')
        print("Offset:" + str(currentOffset) + " Number:" + str(weirdNumber))
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    binary_file.seek(binary_file.tell()-4, 0)
    print("MisteryStructure END offset:" + str(binary_file.tell()))


    # Categories DBName
    # Data     ID    Records TableName Type UID     Version dlcGroup doNotSave Filter name stateData templateValues type unlock_data_int
    # [Start?]                             [UID]
    # EDFE0A00 00000050B009 0000 3F00 0000 92BA0100 4F000000FFFFFFFF5A0000000000000066000030000000006F000030FD06000076000030DE2B000082000050B4090000930000300921 00009A00000000000000 EDFE0000 EDFE0000
    # EDFE0A00 000000500C0A 0000 3F00 0000 6F5C0100 4F000000FFFFFFFF5A0000000000000066000030000000006F00003068070000760000301600000082000050100A0000930000306207 00009A00000000000000 EDFE0000 EDFE0000
    # EDFE0A00 00000050680A 0000 3F00 0000 F97C0100 4F000000FFFFFFFF5A0000000000000066000030000000006F000030790700007600003059010000820000506C0A0000930000306207 00009A00000000000000 EDFE0000 EDFE0000
    # EDFE0A00 00000050C40A 0000 3F00 0000 AFA20100 4F000000FFFFFFFF5A0000000000000066000030000000006F0000308A07000076000030A52B000082000050C80A0000930000306207 00009A00000000000000 EDFE0000 EDFE0000

    print("MisteryStructure2 (separated by 92) START offset:" + str(binary_file.tell())) # To implement 0xEDFE[length(short)][length*8bytes]
    numberOfPatterns=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        weirdDelimiter = binary_file.read(4)
        if weirdDelimiter!=b'\xed\xfe\x0a\x00':
            raise Exception("No delimiter found:" + str(weirdDelimiter) + "at " + str(fieldsStartOffset))
        currentOffset=binary_file.tell()
        firstMistery=binary_file.read(12)
        uid=int.from_bytes(binary_file.read(4), byteorder='little')
        secondMistery=binary_file.read(54)
        thirdMistery=binary_file.read(10)
        firstEdfe=binary_file.read(4)
        secondEdfe=binary_file.read(4)
        print("Pattern:" + str(numberOfPatterns) + " Offset:" + str(currentOffset))
        print("Pattern:" + str(numberOfPatterns) + " firstMistery:" + firstMistery.hex())
        print("Pattern:" + str(numberOfPatterns) + " UID:" + str(uid))
        print("Pattern:" + str(numberOfPatterns) + " secondMistery:" + secondMistery.hex())
        print("Pattern:" + str(numberOfPatterns) + " thirdMistery:" + thirdMistery.hex())
        print("Pattern:" + str(numberOfPatterns) + " firstEdfe:" + firstEdfe.hex())
        print("Pattern:" + str(numberOfPatterns) + " secondEdfe:" + secondEdfe.hex())
        # fieldName=binary_file.read(88)
        # print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " String:" + str(fieldName))
        numberOfPatterns=numberOfPatterns+1
    print("Total patterns:" + str(numberOfPatterns))
    print("MisteryStructure2 END offset:" + str(binary_file.tell()))


    # binary_file.seek(4, 0)
    # numfiles = int.from_bytes(binary_file.read(4), byteorder='little')
    # print("Num files:" + str(numfiles))
