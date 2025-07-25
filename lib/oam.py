import bisect
SPRITE_WIDTHS = ((1,2,4,8),(2,4,4,8),(1,1,2,4)) # in tiles
SPRITE_HEIGHTS = ((1,2,4,8),(1,1,2,4),(2,4,4,8))

class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(data[0x00:0x04], byteorder='little') # entries start at 0x04
        self.address_list = []
        self.fileSize = int.from_bytes(data[0x04+self.entryCount*4:self.entryCount*4+0x08], byteorder='little')
        for index in range(self.entryCount): 
            self.address_list.append(int.from_bytes(data[0x04+index*4:index*4+0x08], byteorder="little")) # 4 bytes per entry
            assert self.address_list[index] < self.fileSize
            if index > 0:
                assert self.address_list[index] >= self.address_list[index-1]

class OAMSection:
    def __init__(self, file: File, index: int):
        self.offset_start = file.address_list[index]
        indexAdd = bisect.bisect_left(file.address_list[index:], self.offset_start+1)
        if index < len(file.address_list)-indexAdd:
            self.offset_end = file.address_list[index+indexAdd]
        else:
            self.offset_end = file.fileSize

        self.data = file.data[self.offset_start:self.offset_end]
        self.header_size = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.header_items = []
        for i in range(0, self.header_size, 4):
            self.header_items.append(int.from_bytes(self.data[i:i+0x04], byteorder='little'))
        self.offsetTable_offset = self.header_size+0x04
        self.constant = int.from_bytes(self.data[self.header_size:self.offsetTable_offset], byteorder='little')
        self.offsetTable_size = int.from_bytes(self.data[self.offsetTable_offset:self.offsetTable_offset+0x02], byteorder='little')
        self.offsetTable = []
        table_small = []
        for i in range(self.offsetTable_offset, self.offsetTable_offset+self.offsetTable_size, 4):
            if i > 0:
                if self.data[i:i+0x02] < self.data[i-0x04:i-0x04+0x02]: # if current offset smaller than prev offset
                    self.offsetTable.append(table_small.copy()) # add current table to animation list
                    #print(f"start: {self.offsetTable}")
                    table_small.clear()
            obj_ptr = int.from_bytes(self.data[i:i+0x02], byteorder='little')
            obj_cnt = int.from_bytes(self.data[i+0x02:i+0x04], byteorder='little')
            #print(f"pointer: {obj_ptr:02X}; count: {obj_cnt:02X};")
            table_small.append([obj_ptr, obj_cnt]) # add frame data to frame list

class Object:
    def __init__(self, data: bytes):
        self.data = data
        self.tileId = int.from_bytes(self.data[0x00:0x01], byteorder='little')
        attributes = int.from_bytes(self.data[0x01:0x02], byteorder='little')
        self.tileId_add = (attributes & 0x03) # * 100
        self.flip_h: bool = (attributes & 0x04) >> 2
        self.flip_v: bool = (attributes & 0x08) >> 3
        self.sizeIndex = (attributes & 0x30) >> 4 # sub-index in SPRITE_WIDTHS and SPRITE_HEIGHTS
        self.shape = (attributes & 0xC0) >> 6 # # index in SPRITE_WIDTHS and SPRITE_HEIGHTS
        self.x = int.from_bytes(self.data[0x02:0x03], byteorder='little', signed=True) # relative to spawn pos
        self.y = int.from_bytes(self.data[0x03:0x04], byteorder='little', signed=True)

    def getWidth(self):
        return SPRITE_WIDTHS[self.shape][self.sizeIndex]
    
    def getHeight(self):
        return SPRITE_HEIGHTS[self.shape][self.sizeIndex]

    def toBytes(self):
        data = bytearray()
        attributes = (self.tileId_add) + (self.flip_h << 2) + (self.flip_v << 3) + (self.sizeIndex << 4) + (self.shape << 6)
        data += int.to_bytes(self.tileId, 1, byteorder="little") + int.to_bytes(attributes, 1, byteorder="little")
        data += int.to_bytes(self.x, 1, byteorder="little", signed=True) + int.to_bytes(self.y, 1, byteorder="little", signed=True)
        print(data.hex())
        return data