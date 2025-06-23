class Font:
    def __init__(self, data):
        self.char_width = int.from_bytes(data[0x00:0x02], "little") # must be an even nubmer
        self.char_height = int.from_bytes(data[0x02:0x04], "little")
        self.indexing_space = int.from_bytes(data[0x04:0x08], "little")
        self.char_count = int.from_bytes(data[0x08:0x0C], "little") # info is not read
        self.file_size = int.from_bytes(data[0x0C:0x10], "little")
        self.unused_string = data[0x10:0x20] # probably path of source bitmap file before it was converted to bin
        self.chr_data = data[0x20:0x20+self.file_size]
