class CharMap:
    def __init__(self):
        self.dict_byte_to_unicode = {}
        self.dict_unicode_to_byte = {}
    
    def add_mapping(self, map_byte: tuple[int], map_unicode: str):
        self.add_byte_mapping(map_byte, map_unicode)
        self.add_unicode_mapping(map_byte, map_unicode)

    def add_byte_mapping(self, map_byte: tuple[int], map_unicode: str):
        if map_byte in self.dict_byte_to_unicode:
            raise RuntimeError(f"a charmap mapping for byte {map_byte} already exists")
        self.dict_byte_to_unicode[map_byte] = map_unicode

    def add_unicode_mapping(self, map_byte: tuple[int], map_unicode: str):
        if map_unicode in self.dict_unicode_to_byte:
            raise RuntimeError(f"a charmap mapping for unicode {map_unicode} already exists")
        self.dict_unicode_to_byte[map_unicode] = map_byte

    def add_mapping_range(self, map_byte: tuple[int], map_unicode: str, length: int):
        list_map_byte = list(map_byte)
        int_map_unicode = ord(map_unicode)
        for i in range(length):
            map_byte = tuple(list_map_byte)
            map_unicode = chr(int_map_unicode)
            self.add_mapping(map_byte, map_unicode)
            list_map_byte[len(map_byte)-1] += 1
            int_map_unicode += 1
    
    def add_byte_mapping_range(self, map_byte: tuple[int], map_unicode: str, length: int):
        list_map_byte = list(map_byte)
        int_map_unicode = ord(map_unicode)
        for i in range(length):
            map_byte = tuple(list_map_byte)
            map_unicode = chr(int_map_unicode)
            self.add_byte_mapping(map_byte, map_unicode)
            list_map_byte[len(map_byte)-1] += 1
            int_map_unicode += 1
    
    def add_unicode_mapping_range(self, map_byte: tuple[int], map_unicode: str, length: int):
        list_map_byte = list(map_byte)
        int_map_unicode = ord(map_unicode)
        for i in range(length):
            map_byte = tuple(list_map_byte)
            map_unicode = chr(int_map_unicode)
            self.add_unicode_mapping(map_byte, map_unicode)
            list_map_byte[len(map_byte)-1] += 1
            int_map_unicode += 1
    
    def get_byte_mapping(self, search_byte: bytearray) -> tuple[str, int]:
        map_byte_list: list[str] = list(self.dict_byte_to_unicode.keys())
        found_map_byte = None
        for i, sb in enumerate(search_byte):
            map_byte_list = [map_byte for map_byte in map_byte_list 
                             if map_byte[i] is None or map_byte[i] == sb]
            if len(map_byte_list) == 1 and i+1 == len(map_byte_list[0]):
                found_map_byte = map_byte_list[0]
                break
            if len(map_byte_list) == 0:
                break
        if found_map_byte is None:
            #raise RuntimeError(f"byte mapping for bytearray {search_byte} was not found")
            search_unicode = f"├0x{search_byte[0]:02X}┤"
            search_byte_len = 1
        else:
            byte_params = []
            for mb, sb in zip(found_map_byte, search_byte):
                if mb is None:
                    byte_params.append(sb)
            
            search_unicode = self.dict_byte_to_unicode[found_map_byte].format(*byte_params)
            search_byte_len = len(found_map_byte)
        return (search_unicode, search_byte_len)
    
    def get_unicode_mapping(self, search_unicode: str) -> tuple[bytearray, int]:
        map_unicode_list: list[str] = list(self.dict_unicode_to_byte.keys())
        if search_unicode[0] == "├":
            search_unicode_len = search_unicode.index("┤") + 1
            search_unicode = search_unicode[:search_unicode_len]
            search_unicode_name = search_unicode.split(" ")[0]
            map_unicode_list = [map_unicode for map_unicode in map_unicode_list 
                                if map_unicode.split(" ")[0] == search_unicode_name]
            if len(map_unicode_list) == 0:
                if search_unicode.startswith("├0x"):
                    found_map_byte = [int(search_unicode[3:-1], 16)]
                else:
                    raise RuntimeError(f"unicode mapping for unicode special command {search_unicode} was not found")
            else:
                found_map_unicode = map_unicode_list[0]
                found_map_byte = self.dict_unicode_to_byte[found_map_unicode]
            search_unicode_params = search_unicode[:-1].split(" ")[1:]
            search_unicode_params = [int(param, 0) for param in search_unicode_params]
            search_byte = bytearray()
            for mb in found_map_byte:
                if mb is None:
                    search_byte.append(search_unicode_params.pop(0))
                else:
                    search_byte.append(mb)
            return (search_byte, search_unicode_len)
        else:
            found_map_unicode = None
            for i, su in enumerate(search_unicode):
                map_unicode_list = [map_unicode for map_unicode in map_unicode_list 
                                    if map_unicode[i] == su]
                if len(map_unicode_list) == 1 and i+1 == len(map_unicode_list[0]):
                    found_map_unicode = map_unicode_list[0]
                    break
                if len(map_unicode_list) == 0:
                    break
            if found_map_unicode is None:
                raise RuntimeError(f"unicode mapping for unicode {search_unicode} was not found")
            found_map_byte = self.dict_unicode_to_byte[found_map_unicode]
            search_unicode_len = len(found_map_unicode)
            search_byte = bytearray(found_map_byte)
            return (search_byte, search_unicode_len)

