from lib import common, datconv
import bisect

SPRITE_WIDTHS = ((1,2,4,8),(2,4,4,8),(1,1,2,4)) # in tiles
SPRITE_HEIGHTS = ((1,2,4,8),(1,1,2,4),(2,4,4,8))
SPRITE_DIMENSIONS = (("1x1", "2x2", "4x4", "8x8"), ("2x1", "4x1", "4x2", "8x4"), ("1x2", "1x4", "2x4", "4x8"))

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class OAMSection:
    def __init__(self, file: File, index: int):
        self.offset_start = file.address_list[index][0]
        indexAdd = bisect.bisect_left([addr[0] for addr in file.address_list[index:]], self.offset_start+1)
        if index < len(file.address_list)-indexAdd:
            self.offset_end = file.address_list[index+indexAdd][0]
        else:
            self.offset_end = file.fileSize

        self.data = file.data[self.offset_start:self.offset_end]
        self.header_size = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.header_items = []
        for i in range(0, self.header_size, 4):
            self.header_items.append(int.from_bytes(self.data[i:i+0x04], byteorder='little'))
        self.frameTable_constant = int.from_bytes(self.data[self.header_items[0]:self.header_items[0]+0x04], byteorder='little')
        self.frameTable_offset = self.header_items[0]+self.frameTable_constant # relative to section
        self.frameTable_size = int.from_bytes(self.data[self.frameTable_offset:self.frameTable_offset+0x02], byteorder='little')
        self.frameTable = []
        for i in range(self.frameTable_offset, self.frameTable_offset+self.frameTable_size, 4):
            obj_ptr = int.from_bytes(self.data[i:i+0x02], byteorder='little')  # oam pointer
            obj_cnt = int.from_bytes(self.data[i+0x02:i+0x03], byteorder='little') # object count
            obj_sec = int.from_bytes(self.data[i+0x03:i+0x04], byteorder='little') # id of gfx section, apparently
            #print(f"pointer: {obj_ptr:02X}; count: {obj_cnt:02X};")
            self.frameTable.append([obj_ptr, obj_cnt, obj_sec]) # add frame data to frame list
        self.animTable_constant = int.from_bytes(self.data[self.header_items[1]:self.header_items[1]+0x04], byteorder='little')
        self.animTable_offset = self.header_items[1]+self.animTable_constant
        self.animTable_size = int.from_bytes(self.data[self.animTable_offset:self.animTable_offset+0x02], byteorder='little')
        self.animTable = []
        for i in range(self.animTable_offset, self.animTable_offset+self.animTable_size, 2):
            self.animTable.append(int.from_bytes(self.data[i:i+0x02], byteorder='little'))
        self.paletteTable = []
        self.unkTable = []
        if len(self.header_items) == 4: # if palette and unk exist
            self.paletteTable_offset = self.header_items[2]
            self.unkTable_offset = self.header_items[3]
            for i in range(self.paletteTable_offset,
                           self.paletteTable_offset+0x200*int.from_bytes(self.data[self.paletteTable_offset:self.paletteTable_offset+1]),
                           0x200):
                self.paletteTable.append(datconv.BGR15_to_ARGB32(self.data[i:i+0x200]))

class Animation:
    def __init__(self, data: bytes, fStart: int):
        self.data = data
        self.isLooping = False
        self.loopStart = 0
        # relative to section
        self.frames_offset = fStart
        self.frames = []
        for i in range(self.frames_offset, len(self.data), 2):
            fIndex = int.from_bytes(self.data[i:i+0x01], byteorder='little')
            fDuration = int.from_bytes(self.data[i+0x01:i+0x02], byteorder='little')
            if len(self.frames) > 0 and (fDuration in [0xFF, 0xFE]): # animation end marker
                if fDuration == 0xFE:
                    self.isLooping = True
                self.loopStart = fIndex
                self.frames.append([fIndex, fDuration])
                break
            else:
                self.frames.append([fIndex, fDuration])
        print(self.frames)

    def fromParent(oam: OAMSection, index: int):
        frames_offset = oam.animTable_offset+int.from_bytes(oam.data[oam.animTable_offset+index*0x02:oam.animTable_offset+index*0x02+0x02], byteorder='little')
        return Animation(oam.data, frames_offset)
    
    def toBytes(self):
        self.frames[-1] = [self.loopStart, 0xFE if self.isLooping else 0xFF]
        data = bytearray([e for l in self.frames for e in l])
        return data

class Object:
    def __init__(self, data: bytes):
        self.data = data
        self.tileId = int.from_bytes(self.data[0x00:0x01], byteorder='little')
        attributes = int.from_bytes(self.data[0x01:0x02], byteorder='little')
        self.tileId_add = (attributes & 0x03) * 0x100
        self.tileId += self.tileId_add
        self.flip_h: bool = (attributes & 0x04) >> 2
        self.flip_v: bool = (attributes & 0x08) >> 3
        self.sizeIndex = (attributes & 0x30) >> 4 # sub-index in SPRITE_WIDTHS and SPRITE_HEIGHTS
        self.shape = (attributes & 0xC0) >> 6 # # index in SPRITE_WIDTHS and SPRITE_HEIGHTS
        self.x = int.from_bytes(self.data[0x02:0x03], byteorder='little', signed=True) # relative to spawn pos
        self.y = int.from_bytes(self.data[0x03:0x04], byteorder='little', signed=True)

    def getWidth(self):
        assert self.shape < len(SPRITE_WIDTHS) # shape 3 is "Prohibited"
        return SPRITE_WIDTHS[self.shape][self.sizeIndex]
    
    def getHeight(self):
        assert self.shape < len(SPRITE_HEIGHTS)
        return SPRITE_HEIGHTS[self.shape][self.sizeIndex]

    def toBytes(self):
        data = bytearray()
        self.tileId -= self.tileId_add
        attributes = (self.tileId_add//0x100) + (self.flip_h << 2) + (self.flip_v << 3) + (self.sizeIndex << 4) + (self.shape << 6)
        data += int.to_bytes(self.tileId, 1, byteorder="little") + int.to_bytes(attributes, 1, byteorder="little")
        data += int.to_bytes(self.x, 1, byteorder="little", signed=True) + int.to_bytes(self.y, 1, byteorder="little", signed=True)
        print(data.hex())
        return data