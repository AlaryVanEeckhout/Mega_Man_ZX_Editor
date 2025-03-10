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
SPECIAL_CHARACTER_LIST[0xf5] = [1, "├REQUESTEND 0x{0:02X}┤"] #same as 0xfe, but does not interrupt current dialogue
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


class DialogueFile():
    def __init__(self, data: bytes, lang: str="en"):
        self.lang = lang
        file_size = int.from_bytes(data[0x00:0x02], "little")
        text_bin_ptr_array_size = int.from_bytes(data[0x02:0x04], "little")
        assert file_size > text_bin_ptr_array_size

        data = data[0x04:file_size+0x04]
        assert data[len(data)-1] == 0xff

        text_bin_ptr_array = []
        for i in range(0, text_bin_ptr_array_size, 2):
            ptr = int.from_bytes(data[i:i+0x02], "little")
            assert ptr < (file_size - text_bin_ptr_array_size)
            text_bin_ptr_array.append(ptr)

        data = data[text_bin_ptr_array_size:]

        self.textAddress_list = []
        self.text_list = []
        self.text_id_list = []
        id = 0
        for i in range(len(text_bin_ptr_array)):
            start = text_bin_ptr_array[i]
            self.textAddress_list.append(start + text_bin_ptr_array_size + 0x04)
            if data[start] == 0xff:
                self.text_id_list.append(None)
                continue
            text = DialogueFile.convertdata_bin_to_text_until_end(data[start:])
            if text in self.text_list:
                self.text_id_list.append(self.text_list.index(text))
                continue
            self.text_list.append(text)
            self.text_id_list.append(id)
            id += 1


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

    def convertdata_bin_to_text_until_end(data: bytearray):
        chars = []
        i=0
        while i < len(data):# while file not fully read
            if data[i] == 0xFE:
                data = ''.join(chars)# join all converted chars into one full string
                return data
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
        raise Exception("no end found for DialogueFile text")
        

    def convertdata_bin_to_text(data: bytearray):
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

    def convertdata_text_to_bin(data: str):
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
                        special_string = file_text[c:DialogueFile.find_matching_paren(file_text, c, {"├": "┤"})+1]
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


    def generate_file_binary(self):
        text_bin_list = []
        text_bin_id_ptr_list = []
        text_bin_size = 0
        for text in self.text_list:
            text_bin = DialogueFile.convertdata_text_to_bin(text)
            text_bin_id_ptr_list.append(text_bin_size)
            text_bin_size += len(text_bin) + 1
            text_bin_list.append(text_bin)

        text_bin_ptr_array = []
        for id in self.text_id_list:
            if id is None:
                text_bin_ptr_array.append(text_bin_size)
                continue
            text_bin_ptr_array.append(text_bin_id_ptr_list[id])

        text_bin_ptr_array_size = len(text_bin_ptr_array)*2
        file_size = text_bin_ptr_array_size + text_bin_size + 1

        assert file_size <= 0xffff

        file_binary = file_size.to_bytes(2, "little") + text_bin_ptr_array_size.to_bytes(2, "little")
        for ptr in text_bin_ptr_array:
            if ptr is None:
                file_binary += text_bin_size.to_bytes(2, "little")
                continue
            file_binary += ptr.to_bytes(2, "little")
        for text_bin in text_bin_list:
            file_binary += text_bin + 0xfe.to_bytes(1)
        return file_binary + 0xff.to_bytes(1)



 #create readable text
#with open("test.txt", "wb") as t:
#    t.write(bytes(DialogueFile.convertfile_bin_to_text("talk_m01_en1.bin"), "utf-8"))
 #create bin file
#with open("talk_m01_en1.bin", "wb") as t:
#    #DialogueFile.convertfile_text_to_bin("test.txt")
#    t.write((DialogueFile.convertfile_text_to_bin("test.txt")))