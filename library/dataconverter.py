#import os.path
#import numpy
#import PIL, PIL.Image
import PyQt6.QtGui
#import io
import enum

#https://www.rapidtables.com/code/text/ascii-table.html
SPECIAL_CHARACTER_LIST: list = ([0])*256
SPECIAL_CHARACTER_LIST[0x5f] = [0, "⠂"]
SPECIAL_CHARACTER_LIST[0x60] = [0, "€"]
#SPECIAL_CHARACTER_LIST[0x61] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x62] = [0, "𐄀"]
#SPECIAL_CHARACTER_LIST[0x63] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x64] = [0, "⠤"]
SPECIAL_CHARACTER_LIST[0x65] = [0, "┅"]
#SPECIAL_CHARACTER_LIST[0x66] = [0, ""] #unknown char, empty in font
#SPECIAL_CHARACTER_LIST[0x67] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x68] = [0, "ˆ"]
#SPECIAL_CHARACTER_LIST[0x69] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x6a] = [0, "Š"]
SPECIAL_CHARACTER_LIST[0x6b] = [0, "⟨"]
SPECIAL_CHARACTER_LIST[0x6c] = [0, "Œ"]
#SPECIAL_CHARACTER_LIST[0x6d] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x6e] = [0, "Ž"]
#SPECIAL_CHARACTER_LIST[0x6f] = [0, ""] #unknown char, empty in font
#SPECIAL_CHARACTER_LIST[0x70] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x71] = [0, "‘"]
SPECIAL_CHARACTER_LIST[0x72] = [0, "’"]
SPECIAL_CHARACTER_LIST[0x73] = [0, "“"]
SPECIAL_CHARACTER_LIST[0x74] = [0, "”"]
SPECIAL_CHARACTER_LIST[0x75] = [0, "•"]
#SPECIAL_CHARACTER_LIST[0x76] = [0, ""] #unknown char, empty in font
#SPECIAL_CHARACTER_LIST[0x77] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x78] = [0, "˜"]
SPECIAL_CHARACTER_LIST[0x79] = [0, "™"]
SPECIAL_CHARACTER_LIST[0x7a] = [0, "š"]
SPECIAL_CHARACTER_LIST[0x7b] = [0, "⟩"]
SPECIAL_CHARACTER_LIST[0x7c] = [0, "œ"]
#SPECIAL_CHARACTER_LIST[0x7d] = [0, ""] #unknown char, empty in font
SPECIAL_CHARACTER_LIST[0x7e] = [0, "ž"]
SPECIAL_CHARACTER_LIST[0x7f] = [0, "Ÿ"]
SPECIAL_CHARACTER_LIST[0xe0] = [0, "├DPAD_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xe1] = [0, "├DPAD_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xe2] = [0, "├BUTTON_A_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xe3] = [0, "├BUTTON_A_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xe4] = [0, "├BUTTON_B_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xe5] = [0, "├BUTTON_B_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xe6] = [0, "├BUTTON_X_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xe7] = [0, "├BUTTON_X_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xe8] = [0, "├BUTTON_Y_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xe9] = [0, "├BUTTON_Y_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xea] = [0, "├BUTTON_L_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xeb] = [0, "├BUTTON_L_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xec] = [0, "├BUTTON_R_LEFT┤"]
SPECIAL_CHARACTER_LIST[0xed] = [0, "├BUTTON_R_RIGHT┤"]
SPECIAL_CHARACTER_LIST[0xee] = [0, "🡅"]
SPECIAL_CHARACTER_LIST[0xef] = [0, "🡇"]
SPECIAL_CHARACTER_LIST[0xf0] = [1, "├CHAR_F 0x{0:02X}┤"] #sets char to 0xF0 + arg
SPECIAL_CHARACTER_LIST[0xf1] = [1, "├COLOR 0x{0:02X}┤"]
SPECIAL_CHARACTER_LIST[0xf2] = [1, "├PLACEMENT 0x{0:02X}┤"]
SPECIAL_CHARACTER_LIST[0xf3] = [1, "├MUGSHOT 0x{0:02X}┤"]
SPECIAL_CHARACTER_LIST[0xf4] = [1, "├ISOLATE 0x{0:02X}┤"] #hides the next char and draws function arguments.
SPECIAL_CHARACTER_LIST[0xf5] = [1, "├NEXTEVENT 0x{0:02X}┤"] #same as 0xfe, but does not interrupt current dialogue
SPECIAL_CHARACTER_LIST[0xf6] = [1, "├TWOCHOICES 0x{0:02X}┤"]
SPECIAL_CHARACTER_LIST[0xf7] = [1, "├ISOLATE2 0x{0:02X}┤"] #same as 0xf4
SPECIAL_CHARACTER_LIST[0xf8] = [1, "├NAME 0x{0:02X}┤"]
SPECIAL_CHARACTER_LIST[0xf9] = [2, "├COUNTER 0x{0:02X} 0x{1:02X}┤"] #dialogue page counter???
SPECIAL_CHARACTER_LIST[0xfa] = [0, "├PLAYERNAME┤"] # writes player name
SPECIAL_CHARACTER_LIST[0xfb] = [0, "├THREECHOICES┤"]
SPECIAL_CHARACTER_LIST[0xfc] = [0, "├NEWLINE┤"]
SPECIAL_CHARACTER_LIST[0xfd] = [0, "├NEWPAGE┤"]
SPECIAL_CHARACTER_LIST[0xfe] = [0, "├END┤"]
SPECIAL_CHARACTER_LIST[0xff] = [0, "├ENDOFFILE┤"] #end of used file (duplicate text is used to fill the rest of the file)

def ceildiv(a, b):
    return -(a // -b)

def signext(n):
    if n == 0:
        return 0
    elif n > 0:
        return 1
    else:
        return -1

def numberToBase(n: int, b: int): # Does not support decimals(not needed anyway atm)
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
    while n:
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
        if b != 0 and (abs(b) <= 10 or abs(e) <= 9):
            string += str(e)
        elif alphanumeric and (abs(b) > 10 or b == 0) and abs(e) < len(symbols):
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
    list_3 = []
    list_final = []
    for e in list_1:
        if not "{" + e + "}" in s: # if not represented in base 10 due to being out of symbol range
            list_2 = list(e)
        else:
            list_2 = [e]
        list_3.extend(list_2)
    for i in list_3:
        if i.isalpha():
            list_final.append(int(symbols.index(i.upper()))*sign)
        else:
            list_final.append(int(i)*sign)
    return list_final

def baseToInt(l: list, b: int):
    int_final = 0
    for i in range(len(l)):
        int_final += l[i]*b**(len(l)-1 - i)
    return int_final

def StrFromNumber(n: int, b: int, alphanum: bool): #for convenience
    return baseToStr(numberToBase(n, b), b, alphanum)

def IntFromStr(s: str, b: int): #for convenience
    return baseToInt(strToBase(s), b)

def StrToAlphanumStr(s: str, b: int, alphanum: bool): #for convenience
    return baseToStr(strToBase(s), b, alphanum)

def str_subgroups(s: str, n: int):
    return [s[i:i+n] for i in range(0, len(s), n)]

def bitstring_to_bytes(s: str):
    v = int(s, 2)
    b = bytearray()
    if v == 0: # if the bitstring has only zeros, make the conversion as well to not loose data
        b.append(v & 0xff)
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def find_matching_paren(s, i, braces=None):
    openers = braces or {"(": ")"}
    closers = {v: k for k, v in openers.items()}
    stack = []
    result = []

    if s[i] not in openers:
        raise ValueError(f"char at index {i} was not an opening brace")

    for ii in range(i, len(s)):
        c = s[ii]

        if c in openers:
            stack.append([c, ii])
        elif c in closers:
            if not stack:
                raise ValueError(f"tried to close brace without an open at position {i}")

            pair, idx = stack.pop()

            if pair != closers[c]:
                raise ValueError(f"mismatched brace at position {i}")

            if idx == i:
                return ii
    
    if stack:
        raise ValueError(f"no closing brace at position {i}")

    return result

def convertdata_bin_to_text(data: bytearray, lang: str="en"):
    chars = []
    i=0
    while i < len(data):# while file not fully read
        if data[i] <= 0x5E or (data[i] >= 0x80 and data[i] <= 0xDF and data[i] not in [0x80, 0x84, 0x85, 0x86, 0x87, 0x8c, 0x8d, 0x8f, 0x92, 0x93, 0x95, 0x96, 0x98, 0x99, 0x9c, 0x9d, 0x9e]):# ASCII chars
            chars.append(chr(data[i] + 0x20 & 0xFF))
        elif type(SPECIAL_CHARACTER_LIST[data[i]]) == type([]):# game specific chars
            special_character = SPECIAL_CHARACTER_LIST[data[i]]
            params = []
            for p in range(special_character[0]):# if char is a "function", append params and count the file chars read
                i+=1
                if i <= len(data)-1: # if not at end of file
                    params.append(data[i])
                else: # if data incomplete
                    #print(params)
                    #print(special_character[1][:special_character[1].replace("0x", "  ", p).find(" 0x")] + "┤")
                    chars.append(special_character[1][:special_character[1].replace("0x", "  ", p).find(" 0x")].format(*params) + "┤")# add the char and insert the incomplete amount of param values
                    data = ''.join(chars)# join all converted chars into one full string
                    return data
            chars.append(special_character[1].format(*params))# add the char and insert the param values, if applicable
        else:# undefined hex values
            chars.append(f"├0x{data[i]:02X}┤")
        i+=1
    data = ''.join(chars)# join all converted chars into one full string
    return data

def convertdata_text_to_bin(data: str, lang: str="en"):
        file_text = data
        file_data = []
        c=0
        while c < len(file_text):
            if file_text[c] == "├": #extra special chars
                if file_text[c+1:c+3] == "0x": # undefined hex values
                    file_data.append(int.to_bytes(int(file_text[c+3:c+5], 16)))
                    c+=len("├0xXX┤")-1
                else:
                    #special_string = file_text[c:file_text.find("┤", c)+1]
                    special_string = file_text[c:find_matching_paren(file_text, c, {"├": "┤"})+1]
                    #print("special: " +special_string)
                    #print(special_string.split(' ')[0])
                    for d in range(len(SPECIAL_CHARACTER_LIST)): # iterate through special chars
                        if type(SPECIAL_CHARACTER_LIST[d]) == type([]) and SPECIAL_CHARACTER_LIST[d][1].split(' ')[0] == special_string.split(' ')[0]: # if special char matches(remove variable 0xXX part to check)
                            file_data.append(int.to_bytes(d))
                            for p in range(SPECIAL_CHARACTER_LIST[d][0]): # iterate through argument count
                                if len(special_string.split())-2 >= p: #if index is within range(to exclude functions with invalid argument count)
                                    if special_string.replace('0x', '').split()[p+1][0] == "├": # if function passed as arg
                                        #print(special_string.replace('0x', '').split())
                                        #print(special_string.replace('0x', '').split()[p+1].replace('┤┤', '┤') + " was not inserted because it is nested.")
                                        for pd in range(len(SPECIAL_CHARACTER_LIST)): # iterate through special chars
                                            #if type(SPECIAL_CHARACTER_LIST[pd]) == type([]):
                                            #    print(SPECIAL_CHARACTER_LIST[pd][1].split()[0].removesuffix('┤') + " VS " + special_string.replace('0x', '').split()[p+1].removesuffix('┤').removesuffix('┤'))
                                            if type(SPECIAL_CHARACTER_LIST[pd]) == type([]) and SPECIAL_CHARACTER_LIST[pd][1].split()[0].removesuffix('┤') == special_string.replace('0x', '').split()[p+1].removesuffix('┤').removesuffix('┤'): # if special char matches(remove variable 0xXX part to check)
                                                file_data.append(int.to_bytes(pd))
                                    elif special_string.replace('0x', '').split()[p+1].find("{") != -1: # args is undefined
                                        print(special_string + ": Missing argument" + str(p) + "! setting to 0x00.")
                                        file_data.append(int.to_bytes(0x00))
                                    else:
                                        #print(p)
                                        #print(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)])
                                        #file_data.append(int.to_bytes(int(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)], 16)))
                                        file_data.append(int.to_bytes(int(special_string.split()[p+1].removesuffix('┤').removesuffix('┤'), 16)))
                            c+=len(special_string)-1
            elif any(file_text[c] in sublist for sublist in SPECIAL_CHARACTER_LIST if isinstance(sublist, list)): #game's extended char table
                for d in range(len(SPECIAL_CHARACTER_LIST)):
                    if type(SPECIAL_CHARACTER_LIST[d]) == type([]) and SPECIAL_CHARACTER_LIST[d][1] == file_text[c]:
                        file_data.append(int.to_bytes(d))
            else: #normal ASCII chars
                file_data.append(int.to_bytes(ord(file_text[c]) - 0x20 & 0xFF))
            c+=1
        file_data = b''.join(file_data)
        return file_data

class CompressionAlgorithmEnum(enum.Enum):

  def __init__(self, id: enum.auto, depth: int):
      self.id = id
      self.depth = depth

  ONEBPP = enum.auto(), 1
  FOURBPP = enum.auto(), 4
  EIGHTBPP = enum.auto(), 8

def convertdata_bin_to_qt(binary_data: bytearray, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tileWidth=8, tileHeight=8): # GBA 4bpp = 4bpp linear reverse order
    
    #file_bits = bin(int.from_bytes(binary_data))[2:]
    file_bits = "".join([bit for byte in binary_data for bit in ("00000000"+(bin(byte)[2:]))[-8:]])
    image_widget = PyQt6.QtGui.QImage(tileWidth, tileHeight, PyQt6.QtGui.QImage.Format.Format_Indexed8)
    image_widget.setColorTable(palette) # 32bit ARGB color format
    image_widget.fill(15)
    #print(file_bits)
    
    match algorithm:
        case CompressionAlgorithmEnum.ONEBPP: # For english 8x16 and JP 16x16 fonts
            file_bits = "".join([file_bits[i:i+8][::-1] for i in range(0, len(file_bits), 8)]) # reverse the order of the bits in each byte
            for pixel_index in range(0, len(str_subgroups(file_bits, algorithm.depth))):
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(str_subgroups(file_bits, algorithm.depth)[pixel_index], 2))
        case CompressionAlgorithmEnum.FOURBPP: # NDS/GBA 4bpp
            for pixel_index in range(0, len(str_subgroups(file_bits, algorithm.depth)), 2):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(str_subgroups(file_bits, algorithm.depth)[pixel_index+1], 2))
                    image_widget.setPixel(x+1, y, int(str_subgroups(file_bits, algorithm.depth)[pixel_index], 2))
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            for pixel_index in range(0, len(str_subgroups(file_bits, algorithm.depth))):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    image_widget.setPixel(x, y, int(str_subgroups(file_bits, algorithm.depth)[pixel_index], 2))
    return image_widget

def convertdata_qt_to_bin(qimage: PyQt6.QtGui.QImage, palette: list[int]=[0xff000000+((0x0b7421*i)%0x1000000) for i in range(256)], algorithm=CompressionAlgorithmEnum.ONEBPP, tileWidth=8, tileHeight=8): # GBA 4bpp = 4bpp linear reverse order
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
            binary_data = bytearray(bitstring_to_bytes(file_bits))
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
                    binary_data += bytearray(bitstring_to_bytes(file_bits))
        case CompressionAlgorithmEnum.EIGHTBPP: # NDS/GBA 8bpp
            for pixel_index in range(0, qimage.size().width()*qimage.size().height()):
                #print(str_subgroups(file_bits, 4)[pixel_index])
                if pixel_index < tileWidth*tileHeight:
                    x = int(pixel_index % tileWidth)
                    y = int(pixel_index / tileWidth)
                    file_bits = bin(palette.index(qimage.pixelColor(x, y).rgba())).removeprefix('0b').zfill(algorithm.depth)
                    binary_data += bytearray(bitstring_to_bytes(file_bits))
    #print("bits: " + file_bits)
    return binary_data

 #create readable text
#with open("test.txt", "wb") as t:
#    t.write(bytes(convertfile_bin_to_text("talk_m01_en1.bin"), "utf-8"))
 #create bin file
#with open("talk_m01_en1.bin", "wb") as t:
#    #convertfile_text_to_bin("test.txt")
#    t.write((convertfile_text_to_bin("test.txt")))

#create readable graphics
#with open("sys_panm.bin", "r+b") as t:
#    read = t.read()
#    print("read: " + read.hex())
    #print("read bin: " + bin(int(read.hex(), 16)).removeprefix('0b'))
    #print("work: ")
#    alg = CompressionAlgorithmEnum.EIGHTBPP
#    print("convert: " + convertdata_qt_to_bin(convertdata_bin_to_qt(read, algorithm=alg), algorithm=alg).hex())
# convert number to int in different formats
#num = 3000000
#base = 99
#print(numberToBase(num, base))
#print(baseToStr(numberToBase(num, base), base, True))
#print(strToBase(baseToStr(numberToBase(num, base), base, True)))
#print(baseToInt(strToBase(baseToStr(numberToBase(num, base), base, True)), base))
#print(baseToInt(strToBase("3000000"), 99))