class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(data[0x00:0x04], byteorder='little') # entries start at 0x04
        self.address_list = []
        for index in range(self.entryCount): 
            self.address_list.append(int.from_bytes(data[0x04+index*4:index*4+0x08], byteorder="little")) # 4 bytes per entry
            if index > 0:
                assert self.address_list[index] & 0xFFFFFF >= self.address_list[index-1] & 0xFFFFFF
        self.fileSize = int.from_bytes(data[0x04+self.entryCount*4:self.entryCount*4+0x08], byteorder='little')

class GraphicSection:
    def __init__(self, file: File, index: int):
        #print(f"index: {index}")
        assert index >= 0
        self.offset_start = file.address_list[index]
        if index < len(file.address_list)-1:
            self.offset_end = file.address_list[index+1]
        else:
            self.offset_end = file.fileSize
        self.data = file.data[self.offset_start:self.offset_end]
        self.header_size = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.unk01 = int.from_bytes(self.data[0x04:0x08], byteorder='little')
        self.unk02 = int.from_bytes(self.data[0x08:0x0C], byteorder='little')
        self.palette_offset = int.from_bytes(self.data[0x0C:0x10], byteorder='little') # offset from this address
        self.palette_size = int.from_bytes(self.data[0x10:0x12], byteorder='little') # usually 0x200? (256 colors)
        self.unk03 = int.from_bytes(self.data[0x12:0x14], byteorder='little') # palette related. 8, 16, or 264