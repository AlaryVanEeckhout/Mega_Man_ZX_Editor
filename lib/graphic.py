from lib import common
import bisect
import ndspy.lz10

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this may not apply to all files
        self.offset_table = self.address_list[0][0]
        self.offset_palette = self.address_list[1][0]
        if self.entryCount == 6:
            self.offset_unk2 = self.address_list[2][0]
            self.offset_unk3 = self.address_list[3][0]
            self.offset_extraGfx = self.address_list[4][0]

class GraphicsTable: # possibly the same data structure as what I identified as GraphicsSection?
    def __init__(self, data: bytes, start:int=0, end:int|None=None):
        self.ENTRY_SIZE = 0x14
        if end == None:
            end = len(data)
        self.offset_start = start
        self.offset_end = end
        self.data = data
        self.table_size = int.from_bytes(self.data[0x00:0x04], 'little')
        assert self.table_size % self.ENTRY_SIZE == 0 and self.table_size > self.ENTRY_SIZE
        self.offsetCount = self.table_size//self.ENTRY_SIZE
        self.offset_list = []
        for i in range(0, self.table_size, self.ENTRY_SIZE):
            self.offset_list.append([ # might be GraphicsHeader?
                int.from_bytes(self.data[i:i+0x04], 'little'),
                int.from_bytes(self.data[i+0x04:i+0x08], 'little'),
                int.from_bytes(self.data[i+0x08:i+0x0C], 'little'),
                int.from_bytes(self.data[i+0x0C:i+0x10], 'little')])
            
    def getAddrOffset(self, index:int):
        return self.offset_start+index*self.ENTRY_SIZE
    
    def getAddr(self, index:int):
        return self.getAddrOffset(index)+self.offset_list[index][0]
    
    def getAddrEnd(self, index:int):
        return self.getAddrOffset(index)+self.offset_list[index][3]+0x0C
    
    def getData(self, index:int):
        return self.data[self.getAddr(index)-self.offset_start:self.getAddrEnd(index)-self.offset_start]
    
    def joinData(self, index_start:int=0, index_end:int|None=None):
        if index_end == None:
            index_end = self.offsetCount-1
        result = bytearray()
        for i in range(index_start, index_end):
            try:
                result += ndspy.lz10.decompress(self.getData(i))
            except Exception:
                result += self.getData(i)
        return result

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
        #print(f"header size: {self.header_size}")
        self.entryCount = self.header_size//0x14
        self.graphics: list[GraphicHeader] = []
        if self.entryCount > 10000:
            print(f"{self.entryCount} is not a reasonable entry count. aborting...")
            return
        for g in range(self.entryCount):
            offset = g*0x14 # 0x14 is the size of one GraphicHeader
            self.graphics.append(GraphicHeader(self.data[offset:offset+0x14], self.offset_start+offset, self.offset_start+offset+0x14))

    def fromParent(file: File, index: int):
        #print(f"index: {index}")
        assert index >= 0
        offset_start = file.address_list[index][0]
        indexAdd = bisect.bisect_left([addr[0] for addr in file.address_list[index:]], offset_start+1)
        if index < len(file.address_list)-indexAdd:
            offset_end = file.address_list[index+indexAdd][0] #hmm... how to deal with duplicate addresses?
            #print(f"{offset_start} : {file.address_list[bisect.bisect_left(file.address_list, offset_start+1)]}")
        else:
            offset_end = file.fileSize
        return GraphicSection(file.data[offset_start:offset_end], offset_start, offset_end)
    
class GraphicHeader:
    def __init__(self, data: bytes, start: int|None=None, end: int|None=None):
        if None in [start, end]:
            start = 0
            end = len(data)
        self.SIZE = 0x14
        self.data = data
        self.offset_start = start # relative to file
        self.offset_end = end
        self.gfx_offset = int.from_bytes(self.data[0x00:0x04], byteorder='little') # offset from this address
        self.gfx_size = int.from_bytes(self.data[0x04:0x06], byteorder='little')
        self.oam_tile_indexing = int.from_bytes(self.data[0x06:0x07], byteorder='little') # related to tile indexing in oam (0=vram indexes, 0x18=1/4 vram indexes)
        self.oam_tile_offset = int.from_bytes(self.data[0x07:0x08], byteorder='little') # as oam tile id
        self.unk08 = int.from_bytes(self.data[0x08:0x09], byteorder='little') # gfx size related???
        self.unk09 = int.from_bytes(self.data[0x09:0x0A], byteorder='little') # gfx format indicator?
        self.ram_palette_offset = int.from_bytes(self.data[0x0A:0x0C], byteorder='little')
        self.palette_offset = int.from_bytes(self.data[0x0C:0x10], byteorder='little') # offset from this address. palettes are usually stored right after the corresponding gfx
        self.palette_size = int.from_bytes(self.data[0x10:0x12], byteorder='little') # in bytes (color count * 2)
        self.depth = int.from_bytes(self.data[0x12:0x13], byteorder='little') # color depth * 2
        self.unk13 = int.from_bytes(self.data[0x13:0x14], byteorder='little') # palette shift?