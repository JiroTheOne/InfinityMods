#! python3
import os
import sys
import struct
# init
filename=sys.argv[1]
file_length_in_bytes = os.path.getsize(filename)
strings = {}

# functions
def parse_edfe(blockName, indent, the_file):
    edfe = the_file.read(2)
    if edfe!=b'\xed\xfe':
        raise Exception(blockName + " not found:" + str(edfe) + "at " + str(the_file.tell()-2))
    edfeCount = int.from_bytes(the_file.read(2), byteorder='little')
    print("  " + blockName + " count: " + str(edfeCount))
    if edfeCount > 0:
      count=0
      for x in range(edfeCount):
        count+=1
        keyleft = the_file.read(2)
        keyright = the_file.read(2)
        isString = False
        isInt = False
        if keyright == b'\x00\x30':
            isString = True
        if keyright == b'\x00\x00':
            isInt = True
        print(indent + "    Key" + str(count) + ": " + keyleft.hex() + keyright.hex())
        value = the_file.read(4)
        if isString:
            stringIdx = int.from_bytes(value, byteorder='little')
            print(indent + "      Val" + str(count) + ": " + str(strings[stringIdx + stringsOffset]))
        elif isInt:
            valueInt = int.from_bytes(value, byteorder='little')
            print(indent + "      Val" + str(count) + ": " + str(valueInt))
        else:
            print(indent + "      Val" + str(count) + ": " + value.hex())

# begin main block
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
        fieldName=binary_file.read(currentFieldSize)
        binary_file.read(1) # skip trailing delimiter byte
        print("Size:" + str(currentFieldSize) + " String:" + str(fieldName))
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    print("Text fields END offset:" + str(binary_file.tell()))

    print("Strings Structure START offset:" + str(binary_file.tell()))
    numberOfFields=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        currentOffset=binary_file.tell()
        currentFieldSize=int.from_bytes(binary_file.read(1), byteorder='little')
        if currentFieldSize == 0 and numberOfFields > 1:
            break # exit while but not if it is first entry
        binary_file.read(1) # start delimiter
        fieldName=binary_file.read(currentFieldSize)
        binary_file.read(1) # end delimiter
        print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " Hex:" + fieldName.hex() + " String:" + str(fieldName) )
        strings[currentOffset] = str(fieldName)
        numberOfFields=numberOfFields+1
    print("Total fields:" + str(numberOfFields))
    binary_file.seek(binary_file.tell()-2, 0) # going back since we have read two bytes more DIRTY HACK
    print("Strings Structure END offset:" + str(binary_file.tell()))

    # we know the next offset from the header
    binary_file.seek(lastOffset)

    offset = str(binary_file.tell())
    sectionDelimiter = binary_file.read(8) # 000000D0 08000000
    if sectionDelimiter!=b'\x00\x00\x00\xD0\x08\x00\x00\x00':
            raise Exception("Section delimiter not found:" + str(sectionDelimiter) + "at " + str(offset))
    print("Section delimiter START offset: " + str(offset))

    parse_edfe("First", "", binary_file)

    parse_edfe("Second", "", binary_file)

    numbersEdfe = binary_file.read(2)
    if numbersEdfe!=b'\xed\xfe':
            raise Exception("Numbers edfe not found:" + str(numbersEdfe) + "at " + str(binary_file.tell()-2))
    numberCount = int.from_bytes(binary_file.read(2), byteorder='little')
    print("Expected Number count: " + str(numberCount))

    print("Section delimiter END offset: " + str(binary_file.tell()))

    print("Numbers Structure (numbers are separated by 92) START offset:" + str(binary_file.tell())) # To implement 0xEDFE[length(short)][length*8bytes]
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
    print("Numbers Structure END offset:" + str(binary_file.tell()))


    # Categories DBName
    # Data     ID    Records TableName Type UID     Version dlcGroup doNotSave Filter name stateData templateValues type unlock_data_int
    # [Start?] [Count]          [Number]          [UID]                                        marker   [filter?] marker   [name]   marker   [stateData] marker            marker   [type]
    # EDFE     0A00    00000050 B0090000 3F000000 92BA0100 4F000000 FFFFFFFF 5A000000 00000000 66000030 00000000  6F000030 FD060000 76000030 DE2B0000    82000050 B4090000 93000030 09210000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE     0A00    00000050 0C0A0000 3F000000 6F5C0100 4F000000 FFFFFFFF 5A000000 00000000 66000030 00000000  6F000030 68070000 76000030 16000000    82000050 100A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE     0A00    00000050 680A0000 3F000000 F97C0100 4F000000 FFFFFFFF 5A000000 00000000 66000030 00000000  6F000030 79070000 76000030 59010000    82000050 6C0A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000
    # EDFE     0A00    00000050 C40A0000 3F000000 AFA20100 4F000000 FFFFFFFF 5A000000 00000000 66000030 00000000  6F000030 8A070000 76000030 A52B0000    82000050 C80A0000 93000030 62070000 9A000000 00000000 EDFE0000 EDFE0000

    print("MisteryStructure2 (separated by 92) START offset:" + str(binary_file.tell())) # To implement 0xEDFE[length(short)][length*8bytes]
    numberOfPatterns=0
    fieldsStartOffset=binary_file.tell()
    while binary_file.tell()<file_length_in_bytes:
        weirdDelimiter = binary_file.read(2)
        if weirdDelimiter!=b'\xed\xfe':
            raise Exception("No delimiter found:" + str(weirdDelimiter) + "at " + str(fieldsStartOffset))

        childCount = int.from_bytes(binary_file.read(2), byteorder='little')
        print("Found Edfe with " + str(childCount) + " children")

        currentOffset=binary_file.tell()
        numberMarker=binary_file.read(4)
        if numberMarker!=b'\x00\x00\x00\x50':
            raise Exception("No number marker found:" + str(numberMarker) + "at " + str(binary_file.tell()))
        numberKey=int.from_bytes(binary_file.read(4), byteorder='little')
        uidMarker=binary_file.read(4)
        uid=int.from_bytes(binary_file.read(4), byteorder='little')
        mistery1Marker=binary_file.read(4)
        mistery1=binary_file.read(4)
        mistery1Int=int.from_bytes(mistery1, byteorder='little')
        mistery2Marker=binary_file.read(4)
        mistery2=binary_file.read(4)
        mistery2Int=int.from_bytes(mistery2, byteorder='little')
        filterMarker=binary_file.read(4)
        filterOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        nameMarker=binary_file.read(4)
        nameOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        stateMarker=binary_file.read(4)
        stateOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        mistery3Marker=binary_file.read(4)
        mistery3=binary_file.read(4)
        mistery3Int=int.from_bytes(mistery3, byteorder='little')
        typeMarker=binary_file.read(4)
        typeOffset=int.from_bytes(binary_file.read(4), byteorder='little')
        mistery4Marker=binary_file.read(4)
        mistery4=binary_file.read(4)
        mistery4Int=int.from_bytes(mistery4, byteorder='little')
        print("Pattern:" + str(numberOfPatterns) + " Offset: " + str(currentOffset))
        print("  Number marker: " + str(numberMarker.hex()))
        print("  Number: " + str(numberKey - 84) + " (" + str(numberKey) + " - 84)") # what is 84 - is it diff in other lock files?
        print("  UID marker :" + uidMarker.hex())
        print("  UID: " + str(uid))
        print("  dlcGroup Marker: " + mistery1Marker.hex() + " [offsetRef?: " + str(mistery1Int) + "]")
        print("  dlcGroup Hex: " + mistery1.hex())
        print("  dlcGroup SignedInt: "  + str(struct.unpack('>i', mistery1)[0]) )
        print("  mistery2Marker: " + mistery2Marker.hex() + " [offsetRef?: " + str(mistery2Int) + "]")
        print("  mistery2: " + mistery2.hex())
        print("  filter field: " + str(filterMarker.hex()) + " [offsetRef: " + str(filterOffset + stringsOffset) + "]")
        print("  filter: " + str(strings[filterOffset + stringsOffset]))
        print("  name field: " + str(nameMarker.hex()) + " [offsetRef: " + str(nameOffset + stringsOffset) + "]")
        print("  name: " + str(strings[nameOffset + stringsOffset]))
        print("  stateData marker :" + stateMarker.hex() + " [offsetRef: " + str(stateOffset + stringsOffset) + "]")
        print("  stateData: " + str(strings[stateOffset + stringsOffset]))
        print("  mistery3marker: " + mistery3Marker.hex() + " [offsetRef?: " + str(mistery3Int) + "]")
        print("  mistery3: " + mistery3.hex())
        print("  type marker: " + typeMarker.hex() + " [offsetRef: " + str(typeOffset + stringsOffset) + "]")
        print("  type: " + str(strings[typeOffset + stringsOffset]))
        print("  mistery4Marker: " + mistery4Marker.hex() + " [offsetRef?: " + str(mistery4Int) + "]")
        print("  mistery4: " + mistery4.hex())
        edfeCount = 0
        while binary_file.tell()<file_length_in_bytes:
            peekEdfe = binary_file.read(2)
            if peekEdfe != b'\xed\xfe':
                break
            binary_file.read(2) # ignore edfe length for now
            peekNext = binary_file.read(4)
            rewind = 4 + len(peekNext)
            binary_file.seek(binary_file.tell()-rewind, 0)
            if peekNext == b'\x00\x00\x00\x50':
                # Next pattern
                break

            parse_edfe("  Edfe" + str(edfeCount), "  ", binary_file)
            edfeCount+=1
            if (binary_file.tell() == file_length_in_bytes):
                break

        # fieldName=binary_file.read(88)
        # print("Offset:" + str(currentOffset) + " Size:" + str(currentFieldSize) + " String:" + str(fieldName))
        numberOfPatterns=numberOfPatterns+1
    print("Total patterns:" + str(numberOfPatterns))
    print("MisteryStructure2 END offset:" + str(binary_file.tell()))


    # binary_file.seek(4, 0)
    # numfiles = int.from_bytes(binary_file.read(4), byteorder='little')
    # print("Num files:" + str(numfiles))
