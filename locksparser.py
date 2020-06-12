#! python3
import os
import sys

# init
filename=sys.argv[1]
file_length_in_bytes = os.path.getsize(filename)
strings = {}

with open(filename, "rb") as binary_file:

    binary_file.seek(0, 0)

    header = binary_file.read(4)
    if header != b'\xcd\xab\x23\x01':
        raise Exception("Wrong header. Please ensure that the file is a valid chd file")
    print(filename + " Header:" + str(header.hex() ))

    offset = str(binary_file.tell())
    extendedHeader = binary_file.read(4)
    print("Header 2:" + str(extendedHeader.hex()) + " Offset:" + offset )

    offset = str(binary_file.tell())
    textOffset = binary_file.read(4)
    print("Text fields offset is:" + str(textOffset.hex()) + " Offset:" + offset )

    offset = str(binary_file.tell())
    fieldsSize = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Text fields block size (in bytes):" + str(fieldsSize) + " Offset:" + offset )

    offset = str(binary_file.tell())
    stringsOffset = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Strings offset is:" + str(stringsOffset) +" "+ str(hex(stringsOffset)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    stringsSize = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Strings fields block size (in bytes):" + str(stringsSize) +" "+ str(hex(stringsSize)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    lastOffset = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Last offset is:" + str(lastOffset) +" "+ str(hex(lastOffset)) + " Offset:" + offset )

    offset = str(binary_file.tell())
    lastSectionSize = int.from_bytes(binary_file.read(4), byteorder='little')
    print("Last section size:" + str(lastSectionSize) +" "+ str(hex(lastSectionSize)) + " Offset:" + offset )

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

    print("Strings Structure START offset:" + str(binary_file.tell()))
    numberOfFields=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        currentOffset=binary_file.tell()
        currentFieldSize=int.from_bytes(binary_file.read(2), byteorder='little')
        if currentFieldSize==0:
            break
        fieldName=binary_file.read(currentFieldSize)
        binary_file.read(1) # skip last byte
        print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " Hex:" + fieldName.hex() + " String:" + str(fieldName) )
        strings[currentOffset] = fieldName
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    binary_file.seek(binary_file.tell()-2, 0) # going back since we have read two bytes more DIRTY HACK
    print("Strings Structure END offset:" + str(binary_file.tell()))

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
    # [Start?]          [Number]          [UID]                                     marker   [filter?] marker   [name]   marker   [stateData] marker            marker   [type]
    # EDFE0A00 00000050 B0090000 3F000000 92BA0100 4F000000FFFFFFFF5A00000000000000 66000030 00000000  6F000030 FD060000 76000030 DE2B0000    82000050 B4090000 93000030 09210000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE0A00 00000050 0C0A0000 3F000000 6F5C0100 4F000000FFFFFFFF5A00000000000000 66000030 00000000  6F000030 68070000 76000030 16000000    82000050 100A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE0A00 00000050 680A0000 3F000000 F97C0100 4F000000FFFFFFFF5A00000000000000 66000030 00000000  6F000030 79070000 76000030 59010000    82000050 6C0A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE0A00 00000050 C40A0000 3F000000 AFA20100 4F000000FFFFFFFF5A00000000000000 66000030 00000000  6F000030 8A070000 76000030 A52B0000    82000050 C80A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000

    print("MisteryStructure2 (separated by 92) START offset:" + str(binary_file.tell())) # To implement 0xEDFE[length(short)][length*8bytes]
    numberOfPatterns=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        weirdDelimiter = binary_file.read(4)
        if weirdDelimiter!=b'\xed\xfe\x0a\x00':
            raise Exception("No delimiter found:" + str(weirdDelimiter) + "at " + str(fieldsStartOffset))
        currentOffset=binary_file.tell()
        numberMarker=binary_file.read(4)
        if numberMarker!=b'\x00\x00\x00\x50':
            raise Exception("No marker found:" + str(numberMarker) + "at " + str(binary_file.tell()))
        numberKey=int.from_bytes(binary_file.read(4), byteorder='little')
        trailingMarker=binary_file.read(4)
        uid=int.from_bytes(binary_file.read(4), byteorder='little')
        secondMistery=binary_file.read(16) # 4f000000ffffffff5a00000000000000
        filterMarker=binary_file.read(4)
        filterOffset=int.from_bytes(binary_file.read(4), byteorder='little')        
        nameMarker=binary_file.read(4)
        nameOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        stateMarker=binary_file.read(4)
        stateOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        misteryMarker=binary_file.read(4)
        misteryOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        typeMarker=binary_file.read(4)
        typeOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        thirdMistery=binary_file.read(8)
        firstEdfe=binary_file.read(4)
        secondEdfe=binary_file.read(4)
        print("Pattern:" + str(numberOfPatterns) + " Offset: " + str(currentOffset))
        print("  Number marker: " + str(numberMarker.hex()))
        print("  Number value: " + str(numberKey) + " - 84 = " + str(numberKey - 84))
        print("  Number closing marker :" + str(trailingMarker.hex()))
        print("  UID: " + str(uid))
        print("  secondMistery: " + secondMistery.hex())
        print("  filter marker: " + str(filterMarker.hex()))
        print("  filter offset: " + str(filterOffset) + " + 204 = " + str(filterOffset + 204))
        print("  filter: ??")
        print("  name marker: " + str(nameMarker.hex()))
        print("  name offset: " + str(nameOffset) + " + 204 = " + str(nameOffset + 204))
        print("  name: " + str(strings[nameOffset + 204]))
        print("  stateData marker :" + str(stateMarker.hex()))
        print("  stateData offset :" + str(stateOffset) + " + 204 = " + str(stateOffset + 204))
        print("  stateData: " + str(strings[stateOffset + 204]))
        print("  mistery marker: " + str(misteryMarker.hex()))
        print("  mistery offset: " + str(misteryOffset) + " + ??? = ???")
        print("  type marker: " + str(typeMarker.hex()))
        print("  type offset: " + str(typeOffset) + " + 204 = " + str(typeOffset + 204))
        print("  type: " + str(strings[typeOffset + 204]))
        print("  thirdMistery: " + thirdMistery.hex())
        print("  firstEdfe: " + firstEdfe.hex())
        print("  secondEdfe: " + secondEdfe.hex())
        # fieldName=binary_file.read(88)
        # print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " String:" + str(fieldName))
        numberOfPatterns=numberOfPatterns+1
    print("Total patterns:" + str(numberOfPatterns))
    print("MisteryStructure2 END offset:" + str(binary_file.tell()))


    # binary_file.seek(4, 0)
    # numfiles = int.from_bytes(binary_file.read(4), byteorder='little')
    # print("Num files:" + str(numfiles))
