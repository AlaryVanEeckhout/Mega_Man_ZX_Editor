import ndspy.lz10
class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(self.data[0x00:0x04], byteorder='little') # entries start at 0x04
        self.level_offset = int.from_bytes(self.data[0x04:0x08], byteorder='little') & 0x00FFFFFF
        self.gfx_offset = int.from_bytes(self.data[0x08:0x0C], byteorder='little') & 0x00FFFFFF
        self.pal_offset = int.from_bytes(self.data[0x0C:0x10], byteorder='little') & 0x00FFFFFF
        self.fileSize = int.from_bytes(self.data[0x04+self.entryCount*0x04:self.entryCount*0x04+0x08], byteorder='little')

class Level: # LZ10 compressed
    def __init__(self, data: bytes):
        self.data = ndspy.lz10.decompress(data)
        self.metaTiles_offset = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.layout_offset = int.from_bytes(self.data[0x04:0x08], byteorder='little')
        self.screens_offset = int.from_bytes(self.data[0x08:0x0C], byteorder='little')
        self.metaTiles: list[list[list[int]]] = []
        for i in range(self.metaTiles_offset, self.layout_offset, 8):
            self.metaTiles.append([[int.from_bytes(self.data[i:i+0x01], byteorder='little'), int.from_bytes(self.data[i+0x01:i+0x02], byteorder='little')],
                                   [int.from_bytes(self.data[i+0x02:i+0x03], byteorder='little'), int.from_bytes(self.data[i+0x03:i+0x04], byteorder='little')],
                                   [int.from_bytes(self.data[i+0x04:i+0x05], byteorder='little'), int.from_bytes(self.data[i+0x05:i+0x06], byteorder='little')],
                                   [int.from_bytes(self.data[i+0x06:i+0x07], byteorder='little'), int.from_bytes(self.data[i+0x07:i+0x08], byteorder='little')]])
        self.layout: list[list[int]] = []
        for i in range(self.layout_offset, self.screens_offset, 2):
            self.layout.append([int.from_bytes(self.data[i:i+0x01], byteorder='little'),
                                int.from_bytes(self.data[i+0x01:i+0x02], byteorder='little')])
        self.screens: list[list[int]] = []
        screenTiles: list[int] = []
        screenTile_index = 0
        for i in range(self.screens_offset, len(self.data), 2):
            screenTiles.append(int.from_bytes(self.data[i:i+0x02], byteorder='little'))
            if screenTile_index>0 and (screenTile_index+1) % (16*12) == 0:
                self.screens.append(screenTiles.copy())
                screenTiles.clear()
            screenTile_index += 1

    def toBytes(self):
        # convert tiles, layout and screens back to bytes
        return ndspy.lz10.compress(self.data)

class PaletteSection:
    def __init__(self, data: bytes):
        try:
            self.data = ndspy.lz10.decompress(data)
        except TypeError:
            self.data = data
        self.palCount = int.from_bytes(self.data[0x00:0x04], 'little')
        self.palettes: list[PaletteHeader] = []
        for i in range(self.palCount):
            self.palettes.append(PaletteHeader(self.data[0x04+i*0x18:i*0x18+0x1C]))
        

    def toBytes(self):
        # convert properties back to bytes
        return ndspy.lz10.compress(self.data)
    
class PaletteHeader:
    def __init__(self, data: bytes):
        self.data = data
        self.palSize = int.from_bytes(self.data[0x00:0x04], 'little')
        self.unk04 = int.from_bytes(self.data[0x04:0x08], 'little')
        self.unk08 = int.from_bytes(self.data[0x08:0x0C], 'little')
        self.palEndOffset = int.from_bytes(self.data[0x0C:0x10], 'little')
        self.unk14 = int.from_bytes(self.data[0x10:0x14], 'little') # from there
        self.palOffset = int.from_bytes(self.data[0x14:0x18], 'little') # relative to section