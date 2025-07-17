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

def BGR15_to_ARGB32(bgr15_palette: bytes):
    argb32_palette = []
    for i in range(0, len(bgr15_palette), 2):
        bgr15_color = int.from_bytes(bgr15_palette[i:i+2], byteorder='little')
        #print(f"{bgr15_color:04X}")
        # bgr15 color is 0b0BBBBBGGGGGRRRRR
        # we must isolate the bits for each channel
        r = bgr15_color & 0b11111
        g = (bgr15_color >> 5) & 0b11111
        b = (bgr15_color >> 10) & 0b11111
        argb32_color = 0xff000000 + ((r * 0xff // 0b11111) << 16) + ((g * 0xff // 0b11111) << 8) + (b * 0xff // 0b11111)
        #print(f"{argb32_color:08X}")
        argb32_palette.append(argb32_color)
    return argb32_palette

def ARGB32_to_BGR15(argb32_palette: list[int]):
    bgr15_palette = bytearray()
    for argb32_color in argb32_palette:
        r = (argb32_color >> 16) & 0x00ff
        g = (argb32_color >> 8) & 0x0000ff
        b = argb32_color & 0x000000ff
        bgr15_color = (r * 0b11111 // 0xff) + ((g * 0b11111 // 0xff) << 5) + ((b * 0b11111 // 0xff) << 10)
        bgr15_palette.extend(bgr15_color.to_bytes(2, byteorder='little'))
    return bytes(bgr15_palette)

# this fonction works with more than one tile now
def binToQt(binary_data: bytearray, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tilesPerRow: int=8, tilesPerColumn: int=8, tileWidth: int=8, tileHeight: int=8): # GBA 4bpp = 4bpp linear reverse order
    #file_bits = bin(int.from_bytes(binary_data))[2:]
    file_bits = "".join([bit for byte in binary_data for bit in bin(byte)[2:].zfill(8)])
    image_widget = PyQt6.QtGui.QImage(tileWidth*tilesPerRow, tileHeight*tilesPerColumn, PyQt6.QtGui.QImage.Format.Format_Indexed8)
    image_widget.setColorTable(palette) # 32bit ARGB color format
    image_widget.fill(15)
    pixel_index = 0
    step = 1 # amount of pixels processed at once
    #print(file_bits)
    
    match algorithm:
        case CompressionAlgorithmEnum.ONEBPP: # For english 8x16 and JP 16x16 fonts
            file_bits = "".join([file_bits[i:i+8][::-1] for i in range(0, len(file_bits), 8)]) # reverse the order of the bits in each byte
            pixel_colors = str_subgroups(file_bits, algorithm.depth) # color indexes to palette
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                    if pixel_index >= len(pixel_colors): return image_widget
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    image_widget.setPixel(tile_x+x, tile_y+y, int(pixel_colors[pixel_index], 2))
                    pixel_index += step
        case CompressionAlgorithmEnum.FOURBPP: # NDS/GBA 4bpp
            pixel_colors = str_subgroups(file_bits, algorithm.depth) # color indexes to palette
            step = 2
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                    if pixel_index >= len(pixel_colors): return image_widget
                    #print(str_subgroups(file_bits, 4)[pixel_index])
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    x2 = int((j+1) % tileWidth)
                    y2 = int((j+1) / tileWidth)
                    image_widget.setPixel(tile_x+x, tile_y+y, int(pixel_colors[pixel_index+1], 2))
                    image_widget.setPixel(tile_x+x2, tile_y+y2, int(pixel_colors[pixel_index], 2))
                    pixel_index += step
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            pixel_colors = str_subgroups(file_bits, algorithm.depth) # color indexes to palette
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                    if pixel_index >= len(pixel_colors): return image_widget
                    #print(str_subgroups(file_bits, 4)[pixel_index])
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    image_widget.setPixel(tile_x+x, tile_y+y, int(pixel_colors[pixel_index], 2))
                    pixel_index += step
    return image_widget

# this fonction works with more than one tile now
def qtToBin(qimage: PyQt6.QtGui.QImage, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tileWidth: int=8, tileHeight: int=8): # GBA 4bpp = 4bpp linear reverse order
    tilesPerRow = qimage.size().width()//tileWidth
    tilesPerColumn = qimage.size().height()//tileHeight

    binary_data = bytearray()
    file_bits = ""
    pixel_index = 0
    step = 1

    match algorithm:
        case CompressionAlgorithmEnum.ONEBPP: # For english 8x16 font
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    file_bits += bin(palette.index(qimage.pixelColor(tile_x+x, tile_y+y).rgba()))[2:].zfill(algorithm.depth)
                    pixel_index += step
            file_bits = "".join([file_bits[i:i+8][::-1] for i in range(0, len(file_bits), 8)]) # reverse the order of the bits in each byte
            binary_data = bytearray(bitstrToBytes(file_bits))
        case CompressionAlgorithmEnum.FOURBPP: # NDS/GBA 4bpp
            step = 2
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                #print(str_subgroups(file_bits, 4)[pixel_index])
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    file_bits = bin(palette.index(qimage.pixelColor(tile_x+x+1, tile_y+y).rgba()))[2:].zfill(algorithm.depth)
                    file_bits += bin(palette.index(qimage.pixelColor(tile_x+x, tile_y+y).rgba()))[2:].zfill(algorithm.depth)
                    #print(file_bits)
                    #print(bitstring_to_bytes(file_bits).hex())
                    binary_data += bytearray(bitstrToBytes(file_bits))
                    pixel_index += step
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            for i in range(tilesPerRow*tilesPerColumn): # iterate through tiles
                tile_x = int(i % tilesPerRow)*tileWidth
                tile_y = int(i / tilesPerRow)*tileHeight
                for j in range(0, tileWidth*tileHeight, step): # iterate through pixels
                #print(str_subgroups(file_bits, 4)[pixel_index])
                    x = int(j % tileWidth)
                    y = int(j / tileWidth)
                    file_bits = bin(palette.index(qimage.pixelColor(tile_x+x, tile_y+y).rgba()))[2:].zfill(algorithm.depth)
                    binary_data += bytearray(bitstrToBytes(file_bits))
                    pixel_index += step
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