import os.path

#https://www.rapidtables.com/code/text/ascii-table.html
special_character_list = ([0])*256
special_character_list[0x5f] = [0, "⠂"]
special_character_list[0x60] = [0, "€"]
#special_character_list[0x61] = [0, ""] #unknown char, empty in font
special_character_list[0x62] = [0, "𐄀"]
#special_character_list[0x63] = [0, ""] #unknown char, empty in font
special_character_list[0x64] = [0, "⠤"]
special_character_list[0x65] = [0, "┅"]
#special_character_list[0x66] = [0, ""] #unknown char, empty in font
#special_character_list[0x67] = [0, ""] #unknown char, empty in font
special_character_list[0x68] = [0, "ˆ"]
#special_character_list[0x69] = [0, ""] #unknown char, empty in font
special_character_list[0x6a] = [0, "š"]
special_character_list[0x6b] = [0, "⟨"]
special_character_list[0x6c] = [0, "Œ"]
#special_character_list[0x6d] = [0, ""] #unknown char, empty in font
special_character_list[0x6e] = [0, "Ž"]
#special_character_list[0x6f] = [0, ""] #unknown char, empty in font
#special_character_list[0x70] = [0, ""] #unknown char, empty in font
special_character_list[0x71] = [0, "‘"]
special_character_list[0x72] = [0, "’"]
special_character_list[0x73] = [0, "“"]
special_character_list[0x74] = [0, "”"]
special_character_list[0x75] = [0, "•"]
#special_character_list[0x76] = [0, ""] #unknown char, empty in font
#special_character_list[0x77] = [0, ""] #unknown char, empty in font
special_character_list[0x78] = [0, "˜"]
special_character_list[0x79] = [0, "™"]
special_character_list[0x7a] = [0, "š"]
special_character_list[0x7b] = [0, "⟩"]
special_character_list[0x7c] = [0, "œ"]
#special_character_list[0x7d] = [0, ""] #unknown char, empty in font
special_character_list[0x7e] = [0, "ž"]
special_character_list[0x7f] = [0, "Ÿ"]
#special_character_list[0x80] = [0, " "] #empty in font
special_character_list[0x81] = [0, "¡"]
special_character_list[0x82] = [0, "¢"]
special_character_list[0x83] = [0, "£"]
#special_character_list[0x84] = [0, "¤"] #empty in font
#special_character_list[0x85] = [0, "¥"] #empty in font
#special_character_list[0x86] = [0, "¦"] #empty in font
#special_character_list[0x87] = [0, "§"] #empty in font
special_character_list[0x88] = [0, "¨"]
special_character_list[0x89] = [0, "©"]
special_character_list[0x8a] = [0, "ª"]
special_character_list[0x8b] = [0, "«"]
#special_character_list[0x8c] = [0, "¬"] #empty in font
#special_character_list[0x8d] = [0, ""] #empty in font
special_character_list[0x8e] = [0, "®"]
#special_character_list[0x8f] = [0, "¯"] #empty in font
special_character_list[0x90] = [0, "°"]
special_character_list[0x91] = [0, "±"]
#special_character_list[0x92] = [0, "²"] #empty in font
#special_character_list[0x93] = [0, "³"] #empty in font
special_character_list[0x94] = [0, "´"]
#special_character_list[0x95] = [0, "µ"] #empty in font
#special_character_list[0x96] = [0, "¶"] #empty in font
special_character_list[0x97] = [0, "·"]
#special_character_list[0x98] = [0, "¸"] #empty in font
#special_character_list[0x99] = [0, "¹"] #empty in font
special_character_list[0x9a] = [0, "º"]
special_character_list[0x9b] = [0, "»"]
#special_character_list[0x9c] = [0, "¼"] #empty in font
#special_character_list[0x9d] = [0, "½"] #empty in font
#special_character_list[0x9e] = [0, "¾"] #empty in font
special_character_list[0x9f] = [0, "¿"]
special_character_list[0xa0] = [0, "À"]
special_character_list[0xa1] = [0, "Á"]
special_character_list[0xa2] = [0, "Â"]
special_character_list[0xa3] = [0, "Ã"]
special_character_list[0xa4] = [0, "Ä"]
special_character_list[0xa5] = [0, "Å"]
special_character_list[0xa6] = [0, "Æ"]
special_character_list[0xa7] = [0, "Ç"]
special_character_list[0xa8] = [0, "È"]
special_character_list[0xa9] = [0, "É"]
special_character_list[0xaa] = [0, "Ê"]
special_character_list[0xab] = [0, "Ë"]
special_character_list[0xac] = [0, "Ì"]
special_character_list[0xad] = [0, "Í"]
special_character_list[0xae] = [0, "Î"]
special_character_list[0xaf] = [0, "Ï"]
special_character_list[0xb0] = [0, "Ð"]
special_character_list[0xb1] = [0, "Ñ"]
special_character_list[0xb2] = [0, "Ò"]
special_character_list[0xb3] = [0, "Ó"]
special_character_list[0xb4] = [0, "Ô"]
special_character_list[0xb5] = [0, "Õ"]
special_character_list[0xb6] = [0, "Ö"]
special_character_list[0xb7] = [0, "×"]
special_character_list[0xb8] = [0, "Ø"]
special_character_list[0xb9] = [0, "Ù"]
special_character_list[0xba] = [0, "Ú"]
special_character_list[0xbb] = [0, "Û"]
special_character_list[0xbc] = [0, "Ü"]
special_character_list[0xbd] = [0, "Ý"]
special_character_list[0xbe] = [0, "Þ"]
special_character_list[0xbf] = [0, "ß"]
special_character_list[0xc0] = [0, "à"]
special_character_list[0xc1] = [0, "á"]
special_character_list[0xc2] = [0, "â"]
special_character_list[0xc3] = [0, "ã"]
special_character_list[0xc4] = [0, "ä"]
special_character_list[0xc5] = [0, "å"]
special_character_list[0xc6] = [0, "æ"]
special_character_list[0xc7] = [0, "ç"]
special_character_list[0xc8] = [0, "è"]
special_character_list[0xc9] = [0, "é"]
special_character_list[0xca] = [0, "ê"]
special_character_list[0xcb] = [0, "ë"]
special_character_list[0xcc] = [0, "ì"]
special_character_list[0xcd] = [0, "í"]
special_character_list[0xce] = [0, "î"]
special_character_list[0xcf] = [0, "ï"]
special_character_list[0xd0] = [0, "ð"]
special_character_list[0xd1] = [0, "ñ"]
special_character_list[0xd2] = [0, "ò"]
special_character_list[0xd3] = [0, "ó"]
special_character_list[0xd4] = [0, "ô"]
special_character_list[0xd5] = [0, "õ"]
special_character_list[0xd6] = [0, "ö"]
special_character_list[0xd7] = [0, "÷"]
special_character_list[0xd8] = [0, "ø"]
special_character_list[0xd9] = [0, "ù"]
special_character_list[0xda] = [0, "ú"]
special_character_list[0xdb] = [0, "û"]
special_character_list[0xdc] = [0, "ü"]
special_character_list[0xdd] = [0, "ỳ"]
special_character_list[0xde] = [0, "þ"]
special_character_list[0xdf] = [0, "ÿ"]
special_character_list[0xe0] = [0, "├DPAD_LEFT┤"]
special_character_list[0xe1] = [0, "├DPAD_RIGHT┤"]
special_character_list[0xe2] = [0, "├BUTTON_A_LEFT┤"]
special_character_list[0xe3] = [0, "├BUTTON_A_RIGHT┤"]
special_character_list[0xe4] = [0, "├BUTTON_B_LEFT┤"]
special_character_list[0xe5] = [0, "├BUTTON_B_RIGHT┤"]
special_character_list[0xe6] = [0, "├BUTTON_X_LEFT┤"]
special_character_list[0xe7] = [0, "├BUTTON_X_RIGHT┤"]
special_character_list[0xe8] = [0, "├BUTTON_Y_LEFT┤"]
special_character_list[0xe9] = [0, "├BUTTON_Y_RIGHT┤"]
special_character_list[0xea] = [0, "├BUTTON_L_LEFT┤"]
special_character_list[0xeb] = [0, "├BUTTON_L_RIGHT┤"]
special_character_list[0xec] = [0, "├BUTTON_R_LEFT┤"]
special_character_list[0xed] = [0, "├BUTTON_R_RIGHT┤"]
special_character_list[0xee] = [0, "🡅"]
special_character_list[0xef] = [0, "🡇"]
special_character_list[0xf0] = [1, "├CHAR_F 0x{0:02X}┤"] #sets char to 0xF0 + arg
special_character_list[0xf1] = [1, "├COLOR 0x{0:02X}┤"]
special_character_list[0xf2] = [1, "├PLACEMENT 0x{0:02X}┤"]
special_character_list[0xf3] = [1, "├MUGSHOT 0x{0:02X}┤"]
#special_character_list[0xf4] = [0, ""]
#special_character_list[0xf5] = [0, ""]
special_character_list[0xf6] = [1, "├TWOCHOICES 0x{0:02X}┤"]
#special_character_list[0xf7] = [0, ""]
special_character_list[0xf8] = [1, "├NAME 0x{0:02X}┤"]
#special_character_list[0xf9] = [2, "├0xF9 0x{0:02X} 0x{1:02X}┤"]
#special_character_list[0xfa] = [0, ""]
special_character_list[0xfb] = [0, "├THREECHOICES┤"]
special_character_list[0xfc] = [0, "├NEWLINE┤"]
special_character_list[0xfd] = [0, "├NEWPAGE┤"]
special_character_list[0xfe] = [0, "├END┤"]
#special_character_list[0xff] = [0, ""]


def convertfile_bin_to_text(bin):
    if os.path.exists(bin):
        with open(bin, "rb") as file:
            file_text = file.read()
            chars = []
            i=0
            while i < len(file_text):
                if file_text[i] <= 0x5E:
                    chars.append(chr(file_text[i] + 0x20 & 0xFF))
                elif type(special_character_list[file_text[i]]) == type([]):
                    special_character = special_character_list[file_text[i]]
                    params = []
                    for j in range(special_character[0]):
                        i+=1
                        params.append(file_text[i])
                    chars.append(special_character[1].format(*params))
                else:
                    chars.append(f"├0x{file_text[i]:02X}┤")
                i+=1
            file_text = ''.join(chars)
            return file_text
    else:
        print("The file you are trying to open doesn't exist!")

def convertfile_text_to_bin(text):
    if os.path.exists(text):
        with open(text, "rb") as file:
            file_text = file.read().decode()
            file_data = []
            c=0
            while c < len(file_text):
                if file_text[c] == "├": #extra special chars
                    if file_text[c+1].isdigit():
                        file_data.append(int.to_bytes(int(file_text[c+3]+file_text[c+4], 16)))
                        c+=len("├0xXX┤")-1
                    else:
                        special_string = file_text[c:file_text.find("┤", c)+1]
                        #print(special_string.split(' ')[0])
                        for d in range(len(special_character_list)):
                            if type(special_character_list[d]) == type([]) and special_character_list[d][1].split(' ')[0] == special_string.split(' ')[0]:
                                file_data.append(int.to_bytes(d))
                                for p in range(special_character_list[d][0]):
                                    #print(p)
                                    #print(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)])
                                    file_data.append(int.to_bytes(int(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)], 16)))
                                c+=len(special_string)-1
                elif any(file_text[c] in sublist for sublist in special_character_list if isinstance(sublist, list)): #game's extended char table
                    for d in range(len(special_character_list)):
                        if type(special_character_list[d]) == type([]) and special_character_list[d][1] == file_text[c]:
                            file_data.append(int.to_bytes(d))
                else: #normal ASCII chars
                    file_data.append(int.to_bytes(ord(file_text[c]) - 0x20 & 0xFF))
                c+=1
            file_data = b''.join(file_data)
            return file_data
    else:
        print("The file you are trying to open doesn't exist!")

def convertdata_bin_to_text(data):
    chars = []
    i=0
    while i < len(data):
        if data[i] <= 0x5E:
            chars.append(chr(data[i] + 0x20 & 0xFF))
        elif type(special_character_list[data[i]]) == type([]):
            special_character = special_character_list[data[i]]
            params = []
            for j in range(special_character[0]):
                i+=1
                params.append(data[i])
            chars.append(special_character[1].format(*params))
        else:
            chars.append(f"├0x{data[i]:02X}┤")
        i+=1
    data = ''.join(chars)
    return data

def convertdata_text_to_bin(data):
        file_text = data
        file_data = []
        c=0
        while c < len(file_text):
            if file_text[c] == "├": #extra special chars
                if file_text[c+1].isdigit():
                    file_data.append(int.to_bytes(int(file_text[c+3]+file_text[c+4], 16)))
                    c+=len("├0xXX┤")-1
                else:
                    special_string = file_text[c:file_text.find("┤", c)+1]
                    #print(special_string.split(' ')[0])
                    for d in range(len(special_character_list)):
                        if type(special_character_list[d]) == type([]) and special_character_list[d][1].split(' ')[0] == special_string.split(' ')[0]:
                            file_data.append(int.to_bytes(d))
                            for p in range(special_character_list[d][0]):
                                #print(p)
                                #print(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)])
                                file_data.append(int.to_bytes(int(file_text[c+len(special_string)+2-(5+p*5)]+file_text[c+len(special_string)+3-(5+p*5)], 16)))
                            c+=len(special_string)-1
            elif any(file_text[c] in sublist for sublist in special_character_list if isinstance(sublist, list)): #game's extended char table
                for d in range(len(special_character_list)):
                    if type(special_character_list[d]) == type([]) and special_character_list[d][1] == file_text[c]:
                        file_data.append(int.to_bytes(d))
            else: #normal ASCII chars
                file_data.append(int.to_bytes(ord(file_text[c]) - 0x20 & 0xFF))
            c+=1
        file_data = b''.join(file_data)
        return file_data

 #create readable text
#with open("test.txt", "wb") as t:
#    t.write(bytes(convertfile_bin_to_text("talk_m01_en1.bin"), "utf-8"))
 #create bin file
#with open("talk_m01_en1.bin", "wb") as t:
#    #convertfile_text_to_bin("test.txt")
#    t.write((convertfile_text_to_bin("test.txt")))