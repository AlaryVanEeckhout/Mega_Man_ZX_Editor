from lib import common
import lib.datconv
import bisect
import ndspy.lz10

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.entryCount < 1: return
        self.offset_table = self.address_list[0][0]
        # this may not apply to all files
        if self.entryCount < 2: return # prevent potential crash
        self.offset_palette = self.address_list[1][0]
        if self.entryCount == 6:
            self.offset_unk2 = self.address_list[2][0]
            self.offset_unk3 = self.address_list[3][0]
            self.offset_extraGfx = self.address_list[4][0]

class DataStructure: # make the initialization with offsets more consistant
    def __init__(self, data: bytes, start: int=0, end: int|None=None):
        if end == None:
            end = start+len(data)
        assert end > start
        self.offset_start = start
        self.offset_end = end
        self.size = self.offset_end - self.offset_start
        self.data = data
        if not isinstance(self.data, (bytes, bytearray)):
            raise TypeError(f"Expected 'bytes' object, got '{type(self.data).__name__}'")
        self._init2()

    def _init2(self):
        raise NotImplementedError("Subclasses must implement _init2")

class GraphicsTable(DataStructure): # possibly the same data structure as what I identified as GraphicsSection?
    def _init2(self):
        self.ENTRY_SIZE = 0x14
        self.padding = 0x8000
        self.table_size = int.from_bytes(self.data[0x00:0x04], 'little')
        assert self.table_size % self.ENTRY_SIZE == 0 and self.table_size >= self.ENTRY_SIZE
        self.offsetCount = self.table_size//self.ENTRY_SIZE
        self.offset_list = []
        for i in range(0, self.table_size, self.ENTRY_SIZE):
            self.offset_list.append([ # might be GraphicsHeader?
                int.from_bytes(self.data[i:i+0x04], 'little'), # start
                int.from_bytes(self.data[i+0x04:i+0x08], 'little'), # size, oam_tile_indexing,  oam_tile_offset
                int.from_bytes(self.data[i+0x08:i+0x0C], 'little'), # RAM offset?
                int.from_bytes(self.data[i+0x0C:i+0x10], 'little')]) # end
                # 00 00 08 00
            
    def getAddrOffset(self, index:int):
        return self.offset_start+index*self.ENTRY_SIZE
    
    def getAddr(self, index:int) -> int:
        return self.getAddrOffset(index)+self.offset_list[index][0]
    
    def getSize(self, index: int) -> int:
        return self.offset_list[index][1] & 0x0000FFFF
    
    def getVRAMIndexing(self, index: int) -> int: # maybe?
        return (self.offset_list[index][1] & 0x00FF0000) >> 0x10
    
    def getVRAMOffset(self, index: int) -> int: # maybe?
        return (self.offset_list[index][1] & 0xFF000000) >> 0x18
    
    def getRAM(self, index: int) -> int:
        return self.offset_list[index][2] & 0x00FFFFFF
    
    def getRAM2(self, index: int) -> int:
        return (self.offset_list[index][2] & 0xFF000000) >> 0x18
    
    def getAddrEnd(self, index:int) -> int:
        return self.getAddrOffset(index)+self.offset_list[index][3]+0x0C
    
    def getData(self, index:int):
        return self.data[self.getAddr(index)-self.offset_start:self.getAddrEnd(index)-self.offset_start]

    def _joinData_iter(self, index: int, result: bytearray=None, result_indexes: list[int]=[]):
        newData = bytearray()
        #if len(newData) > 0: result_indexes.append(len(result))
        result_indexes.append(len(result))
        #print(f"{self.getSize(i):04X}")
        #print(f"{self.getVRAMOffset(i):04X}")
        #print(f"{i} {self.offset_list[i][1]:08X}")
        #print(f"{self.offset_list[i][2]:08X}")
        try:
            newData = ndspy.lz10.decompress(self.getData(index))
            #print("cmp")
        except:
            newData = self.getData(index)
            #print("d")
        result += newData
        # 0x200 VRAM tiles padding aligns gfx correctly to be read
        result += bytearray((-len(result)) & (self.padding-1))
        return (result, result_indexes)
    
    def joinData(self, index_start: int=0, index_end: int|None=None):
        if index_end == None or index_end > self.offsetCount:
            index_end = self.offsetCount
        result = bytearray()
        result_indexes = []#[0]
        for i in range(index_start, index_end):
            self._joinData_iter(i, result, result_indexes)
        return (result, result_indexes)

    def joinData_fromindexes(self, indexes: list[int]):
        result = bytearray()
        result_indexes = []#[0]
        for i in indexes:
            if i == 0xF: # no graphics, apparently
                continue
            if i > self.offsetCount-1:
                print(f"tileset offset index {i} out of range {self.offsetCount}")
                return
            self._joinData_iter(i, result, result_indexes)
        return (result, result_indexes)

class GraphicSection(DataStructure):
    def _init2(self):
        self.header_size = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.graphicHeader_size = 0x14
        if self.header_size % self.graphicHeader_size != 0:
            print(f"GFX Header size does not match entry size, reducing entry size from 0x{self.graphicHeader_size:02X} ", end="")
            self.graphicHeader_size = 0x0C
            print(f"to 0x{self.graphicHeader_size:02X}")
        print(f"GFX Header size: {self.header_size:02X}", f"Entry size: {self.graphicHeader_size:02X}")
        assert self.header_size % self.graphicHeader_size == 0
        assert self.header_size >= self.graphicHeader_size
        #print(f"header size: {self.header_size}")
        self.entryCount = self.header_size//self.graphicHeader_size
        self.graphicHeaders: list[GraphicHeader] = []
        if self.entryCount > 10000:
            print(f"{self.entryCount} is not a reasonable entry count. aborting...")
            self.entryCount = 0 # prevent editor from actually loading them
            self.header_size = self.graphicHeader_size*self.entryCount
            return
        if self.entryCount > 0:
            if self.graphicHeader_size == 0x14:
                gfx_head = GraphicHeader(self.data[0:0+self.graphicHeader_size],
                                                start=self.offset_start+0,
                                                end=self.offset_start+0+self.graphicHeader_size)
                if not gfx_head.depth//2 in [4, 8]: # is the entry size really the default value?
                    print(f"Section gave weird results, reducing entry size from 0x{self.graphicHeader_size:02X} to 0x0C")
                    self.graphicHeader_size = 0x0C
            for offset in range(0, self.header_size, self.graphicHeader_size):
                self.graphicHeaders.append(GraphicHeader(self.data[offset:offset+self.graphicHeader_size],
                                                start=self.offset_start+offset,
                                                end=self.offset_start+offset+self.graphicHeader_size))

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
        return GraphicSection(file.data[offset_start:offset_end], start=offset_start, end=offset_end)

    def getGraphic(self, index: int, offsetAdd: int=0):
        header = self.graphicHeaders[index]
        offset_start = header.offset_start - self.offset_start
        return self.data[offset_start+header.gfx_offset+offsetAdd:offset_start+header.gfx_offset+offsetAdd+header.gfx_size]

    def getPalette(self, index: int):
        header = self.graphicHeaders[index]
        if header.size < 0x14: return []  # empty palette because idk where it is
        pal = [0xffffffff]*header.getPaletteSkip() # shift palette
        offset_start = header.offset_start - self.offset_start
        pal.extend(lib.datconv.BGR15_to_ARGB32(
            self.data[offset_start+header.palette_offset+0x0C:offset_start+header.palette_offset+0x0C+header.palette_size]
            )
        )
        return pal
class GraphicHeader(DataStructure):
    def _init2(self):
        #print(type(self.data))
        self.gfx_offset = int.from_bytes(self.data[0x00:0x04], byteorder='little') # offset from this address
        self.gfx_size = int.from_bytes(self.data[0x04:0x06], byteorder='little')
        self.oam_tile_indexing = int.from_bytes(self.data[0x06:0x07], byteorder='little') # related to tile indexing in oam (0=vram indexes, 0x18=1/4 vram indexes)
        self.oam_tile_offset = int.from_bytes(self.data[0x07:0x08], byteorder='little') # as oam tile id
        if self.size <= 0x8: return
        self.unk08 = int.from_bytes(self.data[0x08:0x09], byteorder='little') # gfx size related???
        self.unk09 = int.from_bytes(self.data[0x09:0x0A], byteorder='little') # gfx format indicator?
        self.ram_palette_offset = int.from_bytes(self.data[0x0A:0x0C], byteorder='little')
        if self.size <= 0xC: return
        self.palette_offset = int.from_bytes(self.data[0x0C:0x10], byteorder='little') # offset from this address. palettes are usually stored right after the corresponding gfx
        self.palette_size = int.from_bytes(self.data[0x10:0x12], byteorder='little') # in bytes (color count * 2)
        self.depth = int.from_bytes(self.data[0x12:0x13], byteorder='little') # color depth * 2
        self.unk13 = int.from_bytes(self.data[0x13:0x14], byteorder='little') # palette shift?

    def getPaletteSkip(self):
        return self.unk13 & 0xf0 if self.size >= 0x14 else 0