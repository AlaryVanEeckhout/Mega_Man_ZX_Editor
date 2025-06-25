class Font:
    def __init__(self, data: bytes):
        self.CHR_ADDRESS = 0x20
        self.char_width = int.from_bytes(data[0x00:0x02], "little") # must be an even nubmer
        self.char_height = int.from_bytes(data[0x02:0x04], "little")
        self.indexing_space = int.from_bytes(data[0x04:0x08], "little")
        self.char_count = int.from_bytes(data[0x08:0x0C], "little") # info is not read; = file_size/indexing_space
        self.file_size = int.from_bytes(data[0x0C:0x10], "little")
        self.unused_string = data[0x10:self.CHR_ADDRESS].decode() # probably path of source bitmap file before it was converted to bin
        self.chr_data = data[self.CHR_ADDRESS:self.CHR_ADDRESS+self.file_size]