# dialogue conversion for english (and japanese scripts eventually)
#https://www.rapidtables.com/code/text/ascii-table.html
SPCHARS_E: list = ([0])*256

SPCHARS_E[0x5f] = [0, "⠂"]
SPCHARS_E[0x60] = [0, "€"]
#SPCHARS_E[0x61] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x62] = [0, "𐄀"]
#SPCHARS_E[0x63] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x64] = [0, "⠤"]
SPCHARS_E[0x65] = [0, "┅"]
#SPCHARS_E[0x66] = [0, ""] #unknown char, empty in font
#SPCHARS_E[0x67] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x68] = [0, "ˆ"]
#SPCHARS_E[0x69] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x6a] = [0, "Š"]
SPCHARS_E[0x6b] = [0, "⟨"]
SPCHARS_E[0x6c] = [0, "Œ"]
#SPCHARS_E[0x6d] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x6e] = [0, "Ž"]
#SPCHARS_E[0x6f] = [0, ""] #unknown char, empty in font
#SPCHARS_E[0x70] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x71] = [0, "‘"]
SPCHARS_E[0x72] = [0, "’"]
SPCHARS_E[0x73] = [0, "“"]
SPCHARS_E[0x74] = [0, "”"]
SPCHARS_E[0x75] = [0, "•"]
#SPCHARS_E[0x76] = [0, ""] #unknown char, empty in font
#SPCHARS_E[0x77] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x78] = [0, "˜"]
SPCHARS_E[0x79] = [0, "™"]
SPCHARS_E[0x7a] = [0, "š"]
SPCHARS_E[0x7b] = [0, "⟩"]
SPCHARS_E[0x7c] = [0, "œ"]
#SPCHARS_E[0x7d] = [0, ""] #unknown char, empty in font
SPCHARS_E[0x7e] = [0, "ž"]
SPCHARS_E[0x7f] = [0, "Ÿ"]

SPCHARS_E[0xe0] = [0, "├DPAD_LEFT┤"]
SPCHARS_E[0xe1] = [0, "├DPAD_RIGHT┤"]
SPCHARS_E[0xe2] = [0, "├BUTTON_A_LEFT┤"]
SPCHARS_E[0xe3] = [0, "├BUTTON_A_RIGHT┤"]
SPCHARS_E[0xe4] = [0, "├BUTTON_B_LEFT┤"]
SPCHARS_E[0xe5] = [0, "├BUTTON_B_RIGHT┤"]
SPCHARS_E[0xe6] = [0, "├BUTTON_X_LEFT┤"]
SPCHARS_E[0xe7] = [0, "├BUTTON_X_RIGHT┤"]
SPCHARS_E[0xe8] = [0, "├BUTTON_Y_LEFT┤"]
SPCHARS_E[0xe9] = [0, "├BUTTON_Y_RIGHT┤"]
SPCHARS_E[0xea] = [0, "├BUTTON_L_LEFT┤"]
SPCHARS_E[0xeb] = [0, "├BUTTON_L_RIGHT┤"]
SPCHARS_E[0xec] = [0, "├BUTTON_R_LEFT┤"]
SPCHARS_E[0xed] = [0, "├BUTTON_R_RIGHT┤"]
SPCHARS_E[0xee] = [0, "🡅"]
SPCHARS_E[0xef] = [0, "🡇"]
SPCHARS_E[0xf0] = [1, "├CHAR_F 0x{0:02X}┤"] #sets char to 0xF0 + arg
SPCHARS_E[0xf1] = [1, "├COLOR 0x{0:02X}┤"]
SPCHARS_E[0xf2] = [1, "├PLACEMENT 0x{0:02X}┤"]
SPCHARS_E[0xf3] = [1, "├MUGSHOT 0x{0:02X}┤"]
SPCHARS_E[0xf4] = [1, "├ISOLATE 0x{0:02X}┤"] #hides the next char and draws function arguments.
SPCHARS_E[0xf5] = [1, "├REQUESTEND 0x{0:02X}┤"] #same as 0xfe, but does not interrupt current dialogue
SPCHARS_E[0xf6] = [1, "├TWOCHOICES 0x{0:02X}┤"]
SPCHARS_E[0xf7] = [1, "├ISOLATE2 0x{0:02X}┤"] #same as 0xf4
SPCHARS_E[0xf8] = [1, "├NAME 0x{0:02X}┤"]
SPCHARS_E[0xf9] = [2, "├COUNTER 0x{0:02X} 0x{1:02X}┤"] #dialogue page counter???
SPCHARS_E[0xfa] = [0, "├PLAYERNAME┤"] # writes player name
SPCHARS_E[0xfb] = [0, "├THREECHOICES┤"]
SPCHARS_E[0xfc] = [0, "├NEWLINE┤"]
SPCHARS_E[0xfd] = [0, "├NEWPAGE┤"]
SPCHARS_E[0xfe] = [0, "├END┤"]
SPCHARS_E[0xff] = [0, "├ENDOFFILE┤"] #end of used file (duplicate text is used to fill the rest of the file)

CHARSF_J: list = ([0])*256
CHARSF_J[0x00] = [0, "、"]
CHARSF_J[0x01] = [0, "‐"]
CHARSF_J[0x02] = [0, "。"]
CHARSF_J[0x03] = [0, "／"]
CHARSF_J[0x04] = [0, "："]
CHARSF_J[0x05] = [0, "〈"]
CHARSF_J[0x06] = [0, "＝"]
CHARSF_J[0x07] = [0, "〉"]
CHARSF_J[0x08] = [0, "？"]
CHARSF_J[0x09] = [0, "［"]
CHARSF_J[0x0A] = [0, "］"]
CHARSF_J[0x0B] = [0, "＿"]
CHARSF_J[0x0C] = [0, "～"]
CHARSF_J[0x0D] = [0, "「"]
CHARSF_J[0x0E] = [0, "」"]
CHARSF_J[0x0F] = [0, "…"]
CHARSF_J[0x10] = [0, "運"]
CHARSF_J[0x11] = [0, "屋"]
CHARSF_J[0x12] = [0, "部"]
CHARSF_J[0x13] = [0, "隊"]
CHARSF_J[0x14] = [0, "合"]
CHARSF_J[0x15] = [0, "流"]
CHARSF_J[0x16] = [0, "本"]
CHARSF_J[0x17] = [0, "社"]
CHARSF_J[0x18] = [0, "何"]
CHARSF_J[0x19] = [0, "者"]
CHARSF_J[0x1A] = [0, "出"]
CHARSF_J[0x1B] = [0, "現"]
CHARSF_J[0x1C] = [0, "原"]
CHARSF_J[0x1D] = [0, "因"]
CHARSF_J[0x1E] = [0, "調"]
CHARSF_J[0x1F] = [0, "査"]
CHARSF_J[0x20] = [0, "子"]
CHARSF_J[0x21] = [0, "生"]
CHARSF_J[0x22] = [0, "命"]
CHARSF_J[0x23] = [0, "体"]
CHARSF_J[0x24] = [0, "戦"]
CHARSF_J[0x25] = [0, "争"]
CHARSF_J[0x26] = [0, "発"]
CHARSF_J[0x27] = [0, "地"]
CHARSF_J[0x28] = [0, "見"]
CHARSF_J[0x29] = [0, "会"]
CHARSF_J[0x2A] = [0, "国"]
CHARSF_J[0x2B] = [0, "助"]
CHARSF_J[0x2C] = [0, "年"]
CHARSF_J[0x2D] = [0, "新"]
CHARSF_J[0x2E] = [0, "今"]
CHARSF_J[0x2F] = [0, "回"]
CHARSF_J[0x30] = [0, "変"]
CHARSF_J[0x31] = [0, "身"]
CHARSF_J[0x32] = [0, "少"]
CHARSF_J[0x33] = [0, "女"]
CHARSF_J[0x34] = [0, "転"]
CHARSF_J[0x35] = [0, "送"]
CHARSF_J[0x36] = [0, "青"]
CHARSF_J[0x37] = [0, "赤"]
CHARSF_J[0x38] = [0, "上"]
CHARSF_J[0x39] = [0, "後"]
CHARSF_J[0x3A] = [0, "世"]
CHARSF_J[0x3B] = [0, "界"]
CHARSF_J[0x3C] = [0, "進"]
CHARSF_J[0x3D] = [0, "化"]
CHARSF_J[0x3E] = [0, "王"]
CHARSF_J[0x3F] = [0, "人"]
CHARSF_J[0x40] = [0, "間"]
CHARSF_J[0x41] = [0, "数"]
CHARSF_J[0x42] = [0, "百"]
CHARSF_J[0x43] = [0, "支"]
CHARSF_J[0x44] = [0, "配"]
CHARSF_J[0x45] = [0, "男"]
CHARSF_J[0x46] = [0, "勇"]
CHARSF_J[0x47] = [0, "気"]
CHARSF_J[0x48] = [0, "前"]
CHARSF_J[0x49] = [0, "闘"]
CHARSF_J[0x4A] = [0, "用"]
CHARSF_J[0x4B] = [0, "時"]
CHARSF_J[0x4C] = [0, "代"]
CHARSF_J[0x4D] = [0, "平"]
CHARSF_J[0x4E] = [0, "和"]
CHARSF_J[0x4F] = [0, "死"]
CHARSF_J[0x50] = [0, "名"]
CHARSF_J[0x51] = [0, "・"] # maybe?
CHARSF_J[0x52] = [0, "血"]
CHARSF_J[0x53] = [0, "下"]
CHARSF_J[0x54] = [0, "左"]
CHARSF_J[0x55] = [0, "右"]
CHARSF_J[0x56] = [0, "├DPAD┤"]
CHARSF_J[0x57] = [0, "├BUTTON_A┤"]
CHARSF_J[0x58] = [0, "├BUTTON_B┤"]
CHARSF_J[0x59] = [0, "├BUTTON_X┤"]
CHARSF_J[0x5A] = [0, "├BUTTON_Y┤"]
CHARSF_J[0x5B] = [0, "├BUTTON_L┤"]
CHARSF_J[0x5C] = [0, "├BUTTON_R┤"]
CHARSF_J[0x5D] = [0, "中"]
CHARSF_J[0x5E] = [0, "開"]
CHARSF_J[0x5F] = [0, "分"]
CHARSF_J[0x60] = [0, "型"]
CHARSF_J[0x61] = [0, "長"]
CHARSF_J[0x62] = [0, "大"]
CHARSF_J[0x63] = [0, "量"]
CHARSF_J[0x64] = [0, "内"]
CHARSF_J[0x65] = [0, "同"]
CHARSF_J[0x66] = [0, "動"]
CHARSF_J[0x67] = [0, "続"]
CHARSF_J[0x68] = [0, "悪"]
CHARSF_J[0x69] = [0, "活"]
CHARSF_J[0x6A] = [0, "利"]
CHARSF_J[0x6B] = [0, "空"]
CHARSF_J[0x6C] = [0, "日"]
CHARSF_J[0x6D] = [0, "産"]
CHARSF_J[0x6E] = [0, "使"]
CHARSF_J[0x6F] = [0, "単"]
CHARSF_J[0x70] = [0, "天"]
CHARSF_J[0x71] = [0, "井"]
CHARSF_J[0x72] = [0, "火"]
CHARSF_J[0x73] = [0, "玉"]
CHARSF_J[0x74] = [0, "一"] # maybe?
CHARSF_J[0x75] = [0, "定"]
CHARSF_J[0x76] = [0, "方"]
CHARSF_J[0x77] = [0, "向"]
CHARSF_J[0x78] = [0, "背"]
CHARSF_J[0x79] = [0, "水"]
CHARSF_J[0x7A] = [0, "両"]
CHARSF_J[0x7B] = [0, "各"]
CHARSF_J[0x7C] = [0, "古"]
CHARSF_J[0x7D] = [0, "電"]
CHARSF_J[0x7E] = [0, "固"]
CHARSF_J[0x7F] = [0, "止"]
CHARSF_J[0x80] = [0, "在"]
CHARSF_J[0x81] = [0, "ー"] # maybe?
CHARSF_J[0x82] = [0, "―"] # maybe?
CHARSF_J[0x83] = [0, "仲"]
CHARSF_J[0x84] = [0, "強"]
CHARSF_J[0x85] = [0, "力"]
CHARSF_J[0x86] = [0, "面"]
CHARSF_J[0x87] = [0, "小"]
CHARSF_J[0x88] = [0, "所"]
CHARSF_J[0x89] = [0, "目"]
CHARSF_J[0x8A] = [0, "々"]
CHARSF_J[0x8B] = [0, "都"]
CHARSF_J[0x8C] = [0, "市"]
CHARSF_J[0x8D] = [0, "伝"]
CHARSF_J[0x8E] = [0, "説"]
CHARSF_J[0x8F] = [0, "入"]
CHARSF_J[0x90] = [0, "魚"]
CHARSF_J[0x91] = [0, "路"]
CHARSF_J[0x92] = [0, "守"]
CHARSF_J[0x93] = [0, "手"]
CHARSF_J[0x94] = [0, "木"]
CHARSF_J[0x95] = [0, "葉"]
CHARSF_J[0x96] = [0, "囗"]
CHARSF_J[0x97] = [0, "重"]
CHARSF_J[0x98] = [0, "半"]
CHARSF_J[0x99] = [0, "正"]
CHARSF_J[0x9A] = [0, "式"]
CHARSF_J[0x9B] = [0, "．"]
CHARSF_J[0x9C] = [0, "⯈"]

class DialogueFile:
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
            text = self.binToText_until_end(data[start:])
            if text in self.text_list:
                self.text_id_list.append(self.text_list.index(text))
                continue
            self.text_list.append(text)
            self.text_id_list.append(id)
            id += 1


    def match_paren(s: str, i: int, braces=None): # find index of closing brace for specified opening brace in string
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

    def binToText_iterate(data: bytearray, chars: list[str], i: int, lang: str="en"):
        if lang == "en" and (data[i] <= 0x5E or (data[i] >= 0x80 and data[i] <= 0xDF and data[i] not in [0x80, 0x84, 0x85, 0x86, 0x87, 0x8c, 0x8d, 0x8f, 0x92, 0x93, 0x95, 0x96, 0x98, 0x99, 0x9c, 0x9d, 0x9e])) \
        or lang == "jp" and (data[i] <= 0xF0):# ASCII chars
            if lang == "en":
                chars.append(chr(data[i] + 0x20 & 0xFF))
            elif lang == "jp":
                if data[i] == 0x00:
                    chars.append(chr(0x3000))
                elif 0x01 <= data[i] <= 0x0A:
                    chars.append(chr(data[i]-0x01 + 0xFF10))
                elif 0xB <= data[i] <= 0x24:
                    chars.append(chr(data[i]-0x0B + 0xFF21))
                elif 0x25 <= data[i] <= 0x3E:
                    chars.append(chr(data[i]-0x25 + 0xFF41))
                elif data[i] == 0x3F:
                    chars.append(chr(0x30FC))
                elif 0x40 <= data[i] <= 0x8E:
                    chars.append(chr(data[i]-0x40 + 0x3041))
                elif 0x8F <= data[i] <= 0x90:
                    chars.append(chr(data[i]-0x8F + 0x3092))
                elif 0x91 <= data[i] <= 0xDF:
                    chars.append(chr(data[i]-0x91 + 0x30A1))
                elif 0xE0 <= data[i] <= 0xE4:
                    chars.append(chr(data[i]-0xE0 + 0x30F2))
                elif 0xE5 <= data[i] <= 0xEF:
                    chars.append(chr(data[i]-0xE5 + 0x0021))
                elif data[i] == 0xF0 and type(CHARSF_J[data[i+1]]) == list:
                    chars.append(CHARSF_J[data[i+1]][1])
                    i+=1 # count 0xF0 command AND the argument
                else:
                    print(f"unhandled char \"{chr(data[i])}\" (0x{data[i]:02X}) !")
                    chars.append(chr(data[i]))
        elif type(SPCHARS_E[data[i]]) == type([]):# game specific chars
            special_character = SPCHARS_E[data[i]]
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
        return [chars, i]

    def binToText_until_end(self, data: bytearray): # used to convert individual messages in file
        chars = []
        i=0
        while i < len(data):# while file not fully read
            if data[i] == 0xFE:
                data = ''.join(chars)# join all converted chars of current page into one full string
                return data
            result = DialogueFile.binToText_iterate(data, chars, i, self.lang)
            if type(result) == bytearray:
                return result
            elif type(result) == list:
                chars, i = result
        raise Exception("no end found for DialogueFile text")
        

    def binToText(data: bytearray, lang="en"): # used when forcing dialogue display state
        chars = []
        i=0
        while i < len(data):# while file not fully read
            result = DialogueFile.binToText_iterate(data, chars, i, lang)
            if type(result) == bytearray:
                return result
            elif type(result) == list:
                chars, i = result
        data = ''.join(chars)# join all converted chars into one full string
        return data

    def textToBin(data: str, lang: str="en"):
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
                        special_string = file_text[c:DialogueFile.match_paren(file_text, c, {"├": "┤"})+1]
                        #print("special: " +special_string)
                        #print(special_string.split(' ')[0])
                        for d in range(len(SPCHARS_E)): # iterate through special chars
                            if type(SPCHARS_E[d]) == type([]) and SPCHARS_E[d][1].split(' ')[0] == special_string.split(' ')[0]: # if special char matches(remove variable 0xXX part to check)
                                file_data.append(int.to_bytes(d))
                                for p in range(SPCHARS_E[d][0]): # iterate through argument count
                                    if len(special_string.split())-2 >= p: #if index is within range(to exclude functions with invalid argument count)
                                        if special_string.replace('0x', '').split()[p+1][0] == "├": # if function passed as arg
                                            #print(special_string.replace('0x', '').split())
                                            #print(special_string.replace('0x', '').split()[p+1].replace('┤┤', '┤') + " was not inserted because it is nested.")
                                            for pd in range(len(SPCHARS_E)): # iterate through special chars
                                                #if type(SPCHARS_E[pd]) == type([]):
                                                #    print(SPCHARS_E[pd][1].split()[0].removesuffix('┤') + " VS " + special_string.replace('0x', '').split()[p+1].removesuffix('┤').removesuffix('┤'))
                                                if type(SPCHARS_E[pd]) == type([]) and SPCHARS_E[pd][1].split()[0].removesuffix('┤') == special_string.replace('0x', '').split()[p+1].removesuffix('┤').removesuffix('┤'): # if special char matches(remove variable 0xXX part to check)
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
                elif lang == "en" and any(file_text[c] in sublist for sublist in SPCHARS_E if isinstance(sublist, list)) \
                or lang == "jp" and any(file_text[c] in sublist for sublist in CHARSF_J if isinstance(sublist, list)): #game's extended char table
                    if lang == "en":
                        for d in range(len(SPCHARS_E)):
                            if type(SPCHARS_E[d]) == type([]) and SPCHARS_E[d][1] == file_text[c]:
                                file_data.append(int.to_bytes(d))
                    elif lang == "jp":
                        for d in range(len(CHARSF_J)):
                            if type(CHARSF_J[d]) == type([]) and CHARSF_J[d][1] == file_text[c]:
                                file_data.append(int.to_bytes(0xF0))
                                file_data.append(int.to_bytes(d))
                else: #normal ASCII chars
                    if lang == "en":
                        file_data.append(int.to_bytes(ord(file_text[c]) - 0x20 & 0xFF))
                    elif lang == "jp":
                        if ord(file_text[c]) == 0x3000:
                            file_data.append(int.to_bytes(0x00))
                        elif 0xFF10 <= ord(file_text[c]) <= 0xFF19:
                            file_data.append(int.to_bytes(ord(file_text[c])-0xFF10 + 0x01))
                        elif 0xFF21 <= ord(file_text[c]) <= 0xFF3A:
                            file_data.append(int.to_bytes(ord(file_text[c])-0xFF21 + 0x0B))
                        elif 0xFF41 <= ord(file_text[c]) <= 0xFF5A:
                            file_data.append(int.to_bytes(ord(file_text[c])-0xFF41 + 0x25))
                        elif ord(file_text[c]) == 0x30FC:
                            file_data.append(int.to_bytes(0x3F))
                        elif 0x3041 <= ord(file_text[c]) <= 0x308F:
                            file_data.append(int.to_bytes(ord(file_text[c])-0x3041 + 0x40))
                        elif 0x3092 <= ord(file_text[c]) <= 0x3093:
                            file_data.append(int.to_bytes(ord(file_text[c])-0x3092 + 0x8F))
                        elif 0x30A1 <= ord(file_text[c]) <= 0x30EF:
                            file_data.append(int.to_bytes(ord(file_text[c])-0x30A1 + 0x91))
                        elif 0x30F2 <= ord(file_text[c]) <= 0x30F6:
                            file_data.append(int.to_bytes(ord(file_text[c])-0x30F2 + 0xE0))
                        elif 0x0021 <= ord(file_text[c]) <= 0x002B:
                            file_data.append(int.to_bytes(ord(file_text[c])-0x0021 + 0xE5))
                        else:
                            print(f"char \"{file_text[c]}\" not directly in font, attempting conversion")
                            if ord(file_text[c]) == 0x0020:
                                file_data.append(int.to_bytes(0x00))
                            elif 0x0030 <= ord(file_text[c]) <= 0x0039:
                                file_data.append(int.to_bytes(ord(file_text[c])-0x0030 + 0x01))
                            elif 0x0041 <= ord(file_text[c]) <= 0x005A:
                                file_data.append(int.to_bytes(ord(file_text[c])-0x0041 + 0x0B))
                            elif 0x0061 <= ord(file_text[c]) <= 0x007A:
                                file_data.append(int.to_bytes(ord(file_text[c])-0x0061 + 0x25))
                            else:
                                print(f"unhandled char \"{file_text[c]}\" (0x{ord(file_text[c]):02X}) !")
                                file_data.append(int.to_bytes(ord(file_text[c]) & 0xEF))
                c+=1
            file_data = b''.join(file_data)
            return file_data


    def toBytes(self):
        text_bin_list = []
        text_bin_id_ptr_list = []
        text_bin_size = 0
        for text in self.text_list:
            text_bin = DialogueFile.textToBin(text, self.lang)
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