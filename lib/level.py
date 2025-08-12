
from lib import common
import ndspy.lz10

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_offset_rom = self.address_list[0] & 0x00FFFFFF
        self.level_offset_indicator = self.address_list[0] & 0xFF000000 # compression indicator
        self.gfx_offset_rom = self.address_list[1] & 0x00FFFFFF
        self.gfx_offset_indicator = self.address_list[1] & 0xFF000000
        self.pal_offset_rom = self.address_list[2] & 0x00FFFFFF
        self.pal_offset_indicator = self.address_list[2] & 0xFF000000
        self.level = Level(self.data[self.level_offset_rom:self.gfx_offset_rom], self.level_offset_indicator == 0x80000000)

    def headerToBytes(self):
        self.data = bytearray()
        self.data += int.to_bytes(self.entryCount, 4, 'little')
        self.data += int.to_bytes(self.level_offset_rom + self.level_offset_indicator, 4, 'little')
        self.data += int.to_bytes(self.gfx_offset_rom + self.gfx_offset_indicator, 4, 'little')
        self.data += int.to_bytes(self.pal_offset_rom + self.pal_offset_indicator, 4, 'little')
        self.data += int.to_bytes(self.fileSize, 4, 'little')
        return bytes(self.data)

class Level: # LZ10 compressed
    def __init__(self, data: bytes, compressed: bool=True):
        if compressed:
            self.data = ndspy.lz10.decompress(data)
        else:
            self.data = data
        self.metaTiles_offset = int.from_bytes(self.data[0x00:0x04], byteorder='little')
        self.collision_offset = int.from_bytes(self.data[0x04:0x08], byteorder='little')
        self.screens_offset = int.from_bytes(self.data[0x08:0x0C], byteorder='little')
        self.metaTiles: list[list[int]] = []
        for i in range(self.metaTiles_offset, self.collision_offset, 8): # 4 tiles in metaTile
            self.metaTiles.append([int.from_bytes(self.data[i:i+0x02], byteorder='little'),
                                   int.from_bytes(self.data[i+0x02:i+0x04], byteorder='little'),
                                   int.from_bytes(self.data[i+0x04:i+0x06], byteorder='little'),
                                   int.from_bytes(self.data[i+0x06:i+0x08], byteorder='little')])
        self.collision: list[list[int]] = []
        for i in range(self.collision_offset, self.screens_offset, 2): # collision shape and attributes
            assert (i-self.collision_offset)//2 < len(self.metaTiles)
            self.collision.append([int.from_bytes(self.data[i:i+0x01], byteorder='little'),
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
        #print(len(self.metaTiles),len(self.collision))

    def toBytes(self):
        self.data = bytearray()
        self.data += int.to_bytes(self.metaTiles_offset, 4, 'little')
        self.data += int.to_bytes(self.collision_offset, 4, 'little')
        self.data += int.to_bytes(self.screens_offset, 4, 'little')
        # convert tiles, collision and screens back to bytes
        self.data.extend([byte for metaTile in self.metaTiles for tile in metaTile for byte in [tile & 0xFF, (tile & 0xFF00) >> 8]])
        self.data.extend([byte for metaTile in self.collision for byte in metaTile])
        self.data.extend([byte for screen in self.screens for metaTileId in screen for byte in [metaTileId & 0xFF, (metaTileId & 0xFF00) >> 8]])
        return ndspy.lz10.compress(self.data) # compression is not as efficient. Resulting file is bigger

class PaletteSection:
    def __init__(self, data: bytes):
        self.animated = False
        try:
            self.data = ndspy.lz10.decompress(data)
        except TypeError:
            print("Animated palette?")
            self.data = data
            self.animated = True
            
        self.palCount = int.from_bytes(self.data[0x00:0x04], 'little')
        assert self.palCount < 0xFF
        self.palettes: list[PaletteHeader] = []

        if self.animated:
            self.paletteOffsets = []
            for i in range(self.palCount):
                self.paletteOffsets.append(int.from_bytes(self.data[0x04+i*0x04:0x08+i*0x04], 'little'))
                self.palettes.append(PaletteHeader(self.data[self.paletteOffsets[i]:self.paletteOffsets[i]+0x18]))
            self.palettes_offset = self.paletteOffsets[-1]+0x18+0x4
        else:
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