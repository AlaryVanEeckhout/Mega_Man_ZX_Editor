class Font:
    CHR_ADDRESS = 0x20
    def __init__(self, data: bytes):
        self.char_width = int.from_bytes(data[0x00:0x02], "little") # must be an even nubmer
        self.char_height = int.from_bytes(data[0x02:0x04], "little")
        self.indexing_space = int.from_bytes(data[0x04:0x08], "little")
        self.char_count = int.from_bytes(data[0x08:0x0C], "little") # info is not read; = file_size/indexing_space
        self.font_size = int.from_bytes(data[0x0C:0x10], "little")
        self.chr_data = data[self.CHR_ADDRESS:self.CHR_ADDRESS+self.font_size]
        try:
            self.unused_string = data[0x10:self.CHR_ADDRESS].decode() # probably path of source bitmap file before it was converted to bin
        except UnicodeDecodeError:
            print("unused string could not be decoded!")