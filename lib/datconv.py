# data converter for numeric bases and for graphics
#import os.path
#import numpy
#import PIL, PIL.Image
import PyQt6.QtGui
#import io
import enum

def ceildiv(a, b):
    return -(a // -b)

def signext(n):
    if n == 0:
        return 0
    elif n > 0:
        return 1
    else:
        return -1

def numToBase(n, b: int, decimals: int=16):
    isfract = False
    if n > 0:
        n2 = n - (n//1) # fractional part
    else:
        n2 = n - ceildiv(n, 1) # fractional part
    if n2 != 0:
        isfract = True
    if n == 0: # 0*n^b = 0
        return [0]
    if b == -1: # Base 1, but even exponents give positive numbers and odd exponents give negative numbers
        if n > 0:
            return [1]+[0, 1]*(n-1)
        else:
            return [1, 0]*-n
    if b == 0: # 0^0 = 1 <=> n = n*0^0; This is essentially a "base infinite" where each number has a different symbol
        return [n]
    if b == 1: # Uses Unary Numeral System
        return [1]*n
    digits = []
    if b < 0: # If base negative, minus equals to number so that the code that follows still works
        n *= -1
        n2 *= -1
    n2_counter = 0
    while n2 != 0 and n2 < 1: #fractionnal
        if n2 < 0 and b > 0:
            digits.append(int(n2 * b - b*signext(n2*b))) # substract to arrive at correct value if not 0
        else:
            digits.append(int(n2 * b))
        n2 = n2*b - int(n2 * b)
        #print("digits: " + str(digits))
        #print(n2)
        if b < 0:
            digits[len(digits)-1] *= -1 # Re-minus equals to number to make it correct sign
        if n2_counter > decimals: # if the amount of digits decoded is starting to be unreasonable
            break
        n2_counter += 1
    if isfract:
        digits.reverse()
        digits.append(".") # separator
    while n: #decimal
        #print(n)
        if n < 0 and b > 0:
            digits.append(int(n % b - b*signext(n%b))) # substract to arrive at correct value if not 0
            n = ceildiv(n, b)
        else:
            digits.append(int(n % b))
            n //= b
        if b < 0:
            digits[len(digits)-1] *= -1 # Re-minus equals to number to make it correct sign
    return digits[::-1]

symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def baseToStr(l: list, b: int, alphanumeric: bool = False):
    string = ""
    for e in l:
        if e == ".":
            string += "."
        elif b != 0 and (abs(b) <= 10 or abs(e) <= 9):
            string += str(e)
        elif alphanumeric and (abs(b) > 10 or b == 0) and abs(e) < len(symbols) and abs(e) < b:
            string += symbols[abs(e)]
        else:
            string += "{" + str(e) + "}" # if out of symbol range, add base 10 value of symbol in curly brackets
    if l[0] < 0: # if negative number, rectify minus symbol
        string = string.replace("-", "")
        string = "-" + string
    string = string
    return string

def strToBase(s: str):
    sign = 1
    if "-" in s:
        sign = -1
    s = s.replace("-", "")
    list_1 = s.replace("{", "}").split("}")
    list_2 = []
    list_final = []
    for e in list_1:
        if not "{" + e + "}" in s: # if not represented in base 10 due to being out of symbol range
            list_2.extend(e) # add e as multiple values
        else:
            list_2.append(e) # add e as one value
    for i in list_2:
        if i == ".":
            list_final.append(i)
        elif i.isalpha():
            list_final.append(int(symbols.index(i.upper()))*sign)
        else:
            list_final.append(int(i)*sign)
    return list_final

def baseToNum(l: list, b: int):
    l2 = l.copy()
    if l2.count(".") > 0:
        l2.remove(".")
    val_final = 0
    #print(l[:l.index(".")])
    for i in range(len(l2)):
        if l.count(".") > 0:
            #print(str(l2[i]) + "*" + str(b) + "^" + str(len(l[:l.index(".")])-1 - i) )
            val_final += l2[i]*b**(len(l[:l.index(".")])-1 - i)
        else:
            val_final += l2[i]*b**(len(l)-1 - i)
    return val_final

def numToStr(n, b: int, alphanum: bool = False): #for convenience
    return baseToStr(numToBase(n, b), b, alphanum)

def strToNum(s: str, b: int): #for convenience
    return baseToNum(strToBase(s), b)

def strSetAlnum(s: str, b: int, alphanum: bool = False): #for convenience
    return baseToStr(strToBase(s), b, alphanum)

def str_subgroups(s: str, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

def bitstrToBytes(s: str):
    b = bytearray()
    l = str_subgroups(s, 8) # separate bitstring into bytes
    for byte in l:
        b.append(int(byte, 2) & 0xff) # convert to hex
    return bytes(b)

class CompressionAlgorithmEnum(enum.Enum):

  def __init__(self, id: enum.auto, depth: int):
      self.id = id
      self.depth = depth

  ONEBPP = enum.auto(), 1
  FOURBPP = enum.auto(), 4
  EIGHTBPP = enum.auto(), 8

def binToQt(binary_data: bytearray, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tileWidth=8, tileHeight=8): # GBA 4bpp = 4bpp linear reverse order
    tileWidth = int(tileWidth)
    tileHeight = int(tileHeight)
    #file_bits = bin(int.from_bytes(binary_data))[2:]
    file_bits = "".join([bit for byte in binary_data for bit in ("00000000"+(bin(byte)[2:]))[-8:]])
    image_widget = PyQt6.QtGui.QImage(tileWidth, tileHeight, PyQt6.QtGui.QImage.Format.Format_Indexed8)
    image_widget.setColorTable(palette) # 32bit ARGB color format
    image_widget.fill(15)
    pixel_colors = [] # color indexes to palette
    #print(file_bits)
    
    match algorithm:
        case CompressionAlgorithmEnum.ONEBPP: # For english 8x16 and JP 16x16 fonts
            file_bits = "".join([file_bits[i:i+8][::-1] for i in range(0, len(file_bits), 8)]) # reverse the order of the bits in each byte
            pixel_colors = str_subgroups(file_bits, algorithm.depth)
            for pixel_index in range(0, len(pixel_colors)):
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(pixel_colors[pixel_index], 2))
        case CompressionAlgorithmEnum.FOURBPP: # NDS/GBA 4bpp
            pixel_colors = str_subgroups(file_bits, algorithm.depth)
            for pixel_index in range(0, len(pixel_colors), 2):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(pixel_colors[pixel_index+1], 2))
                    image_widget.setPixel(x+1, y, int(pixel_colors[pixel_index], 2))
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            pixel_colors = str_subgroups(file_bits, algorithm.depth)
            for pixel_index in range(0, len(pixel_colors)):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(pixel_colors[pixel_index], 2))
    return image_widget

def qtToBin(qimage: PyQt6.QtGui.QImage, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tileWidth=8, tileHeight=8): # GBA 4bpp = 4bpp linear reverse order
    tileWidth = int(tileWidth)
    tileHeight = int(tileHeight)
    binary_data = bytearray()
    file_bits = ""

    match algorithm:
        case CompressionAlgorithmEnum.ONEBPP: # For english 8x16 font
            for pixel_index in range(0, qimage.size().width()*qimage.size().height()):
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    file_bits += bin(palette.index(qimage.pixelColor(x, y).rgba())).removeprefix('0b').zfill(algorithm.depth)
            file_bits = "".join([file_bits[i:i+8][::-1] for i in range(0, len(file_bits), 8)]) # reverse the order of the bits in each byte
            binary_data = bytearray(bitstrToBytes(file_bits))
        case CompressionAlgorithmEnum.FOURBPP: # NDS/GBA 4bpp
            for pixel_index in range(0, qimage.size().width()*qimage.size().height(), 2):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    file_bits = bin(palette.index(qimage.pixelColor(x+1, y).rgba())).removeprefix('0b').zfill(algorithm.depth)
                    file_bits += bin(palette.index(qimage.pixelColor(x, y).rgba())).removeprefix('0b').zfill(algorithm.depth)
                    #print(file_bits)
                    #print(bitstring_to_bytes(file_bits).hex())
                    binary_data += bytearray(bitstrToBytes(file_bits))
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            for pixel_index in range(0, qimage.size().width()*qimage.size().height()):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    file_bits = bin(palette.index(qimage.pixelColor(x, y).rgba())).removeprefix('0b').zfill(algorithm.depth)
                    binary_data += bytearray(bitstrToBytes(file_bits))
    #print("bits: " + file_bits)
    #print("bytearray: " + binary_data.hex())
    return binary_data

#create readable graphics
#with open("sys_panm.bin", "r+b") as t:
#    read = t.read()
#    print("read: " + read.hex())
    #print("read bin: " + bin(int(read.hex(), 16)).removeprefix('0b'))
    #print("work: ")
#    alg = CompressionAlgorithmEnum.EIGHTBPP
#    print("convert: " + convertdata_qt_to_bin(convertdata_bin_to_qt(read, algorithm=alg), algorithm=alg).hex())
# convert number to int in different formats (verify with https://baseconvert.com/)
#num = 65535.9999847412109375
#base = 11
#print("representation")
#print(numberToBase(num, base))
#print(baseToStr(numberToBase(num, base), base, True))
#print(strToBase(baseToStr(numberToBase(num, base), base, True)))
#print("base 10 value = " + str(num))
#print(baseToNum(numberToBase(num, base), base))
#print(baseToNum(strToBase(baseToStr(numberToBase(num, base), base, True)), base))
#print(baseToNum(strToBase(str(num)), base))
#print("normal length:\n0000000000000000\n----------------")
#print(bitstring_to_bytes('00001000'+'00000000'+'00001000'+'00000000'+'00010000'+'00000000'+'00000000'+'00000000').hex())