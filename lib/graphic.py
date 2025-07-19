class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(data[0x00:0x04], byteorder='little') # entries start at 0x04
        self.address_list = []
        self.fileSize = int.from_bytes(data[0x04+self.entryCount*4:self.entryCount*4+0x08], byteorder='little')
        for index in range(self.entryCount): 
            self.address_list.append(int.from_bytes(data[0x04+index*4:index*4+0x08], byteorder="little") & 0xFFFFFF) # 4 bytes per entry
            assert self.address_list[index] & 0xFFFFFF < self.fileSize
            if index > 0:
                assert self.address_list[index] & 0xFFFFFF >= self.address_list[index-1] & 0xFFFFFF

class GraphicSection:
    def __init__(self, data: bytes, start: int|None=None, end: int|None=None):
        #print(f"index: {index}")
        self.data = data
        if start == None:
            self.offset_start = 0
            self.offset_end = len(self.data)
        else:
            self.offset_start = start # relative to file
            self.offset_end = end
        self.header_size = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.entryCount = self.header_size//0x14
        self.graphics: list[GraphicHeader] = []
        for g in range(self.entryCount):
            offset = g*0x14 # 0x14 is the size of one GraphicHeader
            self.graphics.append(GraphicHeader(self.data[offset:offset+0x14], self.offset_start+offset, self.offset_start+offset+0x14))

    def fromParent(file: File, index: int):
        #print(f"index: {index}")
        assert index >= 0
        offset_start = file.address_list[index]
        if index < len(file.address_list)-1:
            offset_end = file.address_list[index+1]
        else:
            offset_end = file.fileSize
        return GraphicSection(file.data[offset_start:offset_end], offset_start, offset_end)
    
class GraphicHeader:
    def __init__(self, data: bytes, start: int, end: int):
        self.SIZE = 0x14
        self.data = data
        self.offset_start = start # relative to file
        self.offset_end = end
        self.gfx_offset = int.from_bytes(self.data[0x00:0x04], byteorder='little') # offset from this address
        self.gfx_size = int.from_bytes(self.data[0x04:0x06], byteorder='little')
        self.ram_gfx_offset = int.from_bytes(self.data[0x06:0x08], byteorder='little')
        self.unk08 = int.from_bytes(self.data[0x08:0x0A], byteorder='little')
        self.ram_palette_offset = int.from_bytes(self.data[0x0A:0x0C], byteorder='little')
        self.palette_offset = int.from_bytes(self.data[0x0C:0x10], byteorder='little') # offset from this address. palettes are usually stored right after the corresponding gfx
        self.palette_size = int.from_bytes(self.data[0x10:0x12], byteorder='little') # usually 0x200? (256 colors)
        self.unk12 = int.from_bytes(self.data[0x12:0x14], byteorder='little') # palette related. 8, 16, or 264