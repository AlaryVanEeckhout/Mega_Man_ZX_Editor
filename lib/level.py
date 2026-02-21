
from lib import common
import ndspy.lz10

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_offset_rom = self.address_list[0][0]
        self.level_offset_attr = self.address_list[0][1] # compression indicator
        self.gfx_offset_rom = self.address_list[1][0]
        self.gfx_offset_attr = self.address_list[1][1]
        self.pal_offset_rom = self.address_list[2][0]
        self.pal_offset_attr = self.address_list[2][1]
        self.levels: list[Level] = []
        try:
            self.level = Level(self.data[self.level_offset_rom:self.gfx_offset_rom], self.level_offset_attr == 0x80)
            self.levels.append(self.level)
        except TypeError:
                print("failed to load normal level")
        if self.entryCount == 7:
            # Model PX and LX scanner map data
            try:
                self.level_radar = Level(self.data[self.address_list[6][0]:], self.address_list[6][1] == 0x80)
                self.levels.append(self.level_radar)
            except TypeError:
                print("failed to load radar level")
            

    def headerToBytes(self):
        self.data = bytearray()
        self.data += int.to_bytes(self.entryCount, 4, 'little')
        self.data += int.to_bytes(self.level_offset_rom, 3, 'little')
        self.data += int.to_bytes(self.level_offset_attr, 1, 'little')
        self.data += int.to_bytes(self.gfx_offset_rom, 3, 'little')
        self.data += int.to_bytes(self.gfx_offset_attr, 1, 'little')
        self.data += int.to_bytes(self.pal_offset_rom, 3, 'little')
        self.data += int.to_bytes(self.pal_offset_attr, 1, 'little')
        if self.entryCount == 7:
            # placeholder for when the pointers will have unique variable names
            self.data += int.to_bytes(self.address_list[3][0], 3, 'little') # sky mapping?
            self.data += int.to_bytes(self.address_list[3][1], 1, 'little')
            self.data += int.to_bytes(self.address_list[4][0], 3, 'little') # animated palettes
            self.data += int.to_bytes(self.address_list[4][1], 1, 'little')
            self.data += int.to_bytes(self.address_list[5][0], 3, 'little') # palette animations
            self.data += int.to_bytes(self.address_list[5][1], 1, 'little')
            self.data += int.to_bytes(self.address_list[6][0], 3, 'little') # radar level
            self.data += int.to_bytes(self.address_list[6][1], 1, 'little')
        self.data += int.to_bytes(self.fileSize, 4, 'little')
        return bytes(self.data)

class Overlay:
    def __init__(self, data: bytes, baseRAMAddress: int, structRAMAddress: int, entitySlotRAMAddress: int, entityCoordRAMAddress: int):
        self.data = data
        self.RAMAddress = baseRAMAddress

        self.struct_RAMAddress = structRAMAddress
        self.struct_address = self.getFileAddress(self.struct_RAMAddress)
        self.entityCoord_RAMAddress = entityCoordRAMAddress
        self.entityCoord_address = self.getFileAddress(self.entityCoord_RAMAddress)
        self.entitySlot_RAMAddress = entitySlotRAMAddress
        self.entitySlot_address = self.getFileAddress(self.entitySlot_RAMAddress)


        print(f"0x{self.struct_RAMAddress:08X}")

        self.firstTable_RAMAddress = int.from_bytes(self.data[self.struct_address+0x04:self.struct_address+0x08], byteorder='little')
        self.tileset_RAMAddress = int.from_bytes(self.data[self.struct_address+0x08:self.struct_address+0x10], byteorder='little')
        if self.tileset_RAMAddress != 0:
            self.tileset_name = data[self.getFileAddress(self.tileset_RAMAddress):self.getFileAddress(self.tileset_RAMAddress)+0x08].decode().replace("\x00", "")
        else:
            self.tileset_name = ""
        self.screenLayout0_RAMAddress = int.from_bytes(self.data[self.struct_address+0x10:self.struct_address+0x14], byteorder='little')
        self.screenLayout1_RAMAddress = int.from_bytes(self.data[self.struct_address+0x14:self.struct_address+0x18], byteorder='little')
        self.screenLayout2_RAMAddress = int.from_bytes(self.data[self.struct_address+0x18:self.struct_address+0x1C], byteorder='little')
        self.screenLayout3_RAMAddress = int.from_bytes(self.data[self.struct_address+0x1C:self.struct_address+0x20], byteorder='little')
        self.screenLayout_radar_RAMAddress = int.from_bytes(self.data[self.struct_address+0x20:self.struct_address+0x24], byteorder='little')
        self.map_tilesetOffset_RAMAddress = int.from_bytes(self.data[self.struct_address+0xC8:self.struct_address+0xCC], byteorder='little') # maybe?
        self.unk_RAMAddress = int.from_bytes(self.data[self.struct_address+0xEC:self.struct_address+0xF0], byteorder='little')
        self.map_behavior_RAMAddress = int.from_bytes(self.data[self.struct_address+0xF0:self.struct_address+0xF4], byteorder='little') # maybe?
        self.screenLayout_camera_RAMAddress = int.from_bytes(self.data[self.struct_address+0xF4:self.struct_address+0xF8], byteorder='little')

        print(f"0x{self.screenLayout0_RAMAddress:08X}: layout0")
        self.screenLayout0 = ScreenLayout(self.data, self.getFileAddress(self.screenLayout0_RAMAddress))
        print(f"0x{self.screenLayout1_RAMAddress:08X}: layout1")
        self.screenLayout1 = ScreenLayout(self.data, self.getFileAddress(self.screenLayout1_RAMAddress))
        print(f"0x{self.screenLayout2_RAMAddress:08X}: layout2")
        self.screenLayout2 = ScreenLayout(self.data, self.getFileAddress(self.screenLayout2_RAMAddress))
        print(f"0x{self.screenLayout3_RAMAddress:08X}: layout3")
        self.screenLayout3 = ScreenLayout(self.data, self.getFileAddress(self.screenLayout3_RAMAddress))
        print(f"0x{self.map_tilesetOffset_RAMAddress:08X}: layout radar")
        self.screenLayout_radar = ScreenLayout(self.data, self.getFileAddress(self.screenLayout_radar_RAMAddress))
        print(f"0x{self.map_tilesetOffset_RAMAddress:08X}: map tilesetOffset (?)")
        self.map_tilesetOffset = ScreenMap(self.data, self.getFileAddress(self.map_tilesetOffset_RAMAddress))
        print(f"0x{self.map_behavior_RAMAddress:08X}: map behavior (?)")
        self.map_behavior = ScreenMap(self.data, self.getFileAddress(self.map_behavior_RAMAddress))
        print(f"0x{self.screenLayout_camera_RAMAddress:08X}: layout camera")
        self.screenLayout_camera = ScreenLayout(self.data, self.getFileAddress(self.screenLayout_camera_RAMAddress), loadReal=False)

        print("Entities")
        print(f"0x{self.entityCoord_RAMAddress:08X}")

        # todo: identify enemies based on id
        self.entities = Entities(self.data, self.entitySlot_address, self.entityCoord_address)

    def getFileAddress(self, RAMAddress: int):
        return RAMAddress - self.RAMAddress

class ScreenLayout:
    def __init__(self, data: bytes, address: int, loadReal: bool=True):
        self.data = data
        self.realWidth = int.from_bytes(data[address:address+0x01], byteorder='little') # width used to load screens with correct alignment
        self.skip = int.from_bytes(data[address+0x01:address+0x02], byteorder='little') # idk
        self.width = int.from_bytes(data[address+0x02:address+0x03], byteorder='little') # width of used portion of layout
        self.height = int.from_bytes(data[address+0x03:address+0x04], byteorder='little')
        loadWidth = self.realWidth if loadReal else self.width
        self.layout: list[list[int]] = []
        layoutRow = []
        print(self.realWidth, self.skip, self.width, self.height)

        for i in range(address+0x04, address+0x04+loadWidth*self.height):
            layoutRow.append(int.from_bytes(self.data[i:i+0x01], byteorder='little'))
            if len(layoutRow) == loadWidth:
                self.layout.append(layoutRow.copy())
                layoutRow.clear()
        print([[f"{screenID:02X}" for screenID in row] for row in self.layout])

class ScreenMap:
    def __init__(self, data: bytes, address: int):
        self.data = data
        self.realWidth = int.from_bytes(data[address:address+0x02], byteorder='little') # width used to define effective screen space
        self.skip = int.from_bytes(data[address+0x02:address+0x04], byteorder='little') # idk
        self.width = int.from_bytes(data[address+0x04:address+0x06], byteorder='little') # width used to load all screens
        self.height = int.from_bytes(data[address+0x06:address+0x08], byteorder='little')
        self.layout: list[list[int]] = []
        layoutRow = []
        print(self.realWidth, self.skip, self.width, self.height)

        for i in range(address+0x08, address+0x08+self.width*self.height*0x02, 0x02):
            layoutRow.append(int.from_bytes(self.data[i:i+0x02], byteorder='little'))
            if len(layoutRow) == self.width:
                self.layout.append(layoutRow.copy())
                layoutRow.clear()
        print([[f"{screenID:04X}" for screenID in row] for row in self.layout])

class Entities:
    def __init__(self, data: bytes, entitySlotaddress: int, entityCoordAddress: int):
        self.data = data
        if entitySlotaddress > 0:
            self.slots = EntitySlots(self.data, entitySlotaddress)
            print(self.slots.entityList)
        if entityCoordAddress > 0:
            self.coords = EntityCoordinates(self.data, entityCoordAddress)
            print(self.coords.entityList)

class EntitySlots:
    def __init__(self, data: bytes, address: int):
        ENTITYKINDS = {
            0x02: "Enemy",
            0x05: "Background",
            0x06: "Item"
        }
        self.data = data
        self.bytesList = []
        self.entityList: list[dict] = []
        index = address
        while True:
            entity_data = self.data[index:index+0x0C]
            if len(entity_data) != 0x0C or entity_data[11] != 0x00: # idk if this is the right way to see if structure ends
                print(entity_data.hex())
                break
            self.bytesList.append(entity_data)
            self.entityList.append({
                "kind": ENTITYKINDS[entity_data[1]] if entity_data[1] in ENTITYKINDS else str(entity_data[1])
            })
            index += 0x0C

class EntityCoordinates:
    def __init__(self, data: bytes, address: int):
        self.data = data
        self.startOffset = address
        self.endOffset = self.startOffset + self.data[self.startOffset:].find(bytes.fromhex("FFFFFF7FFF7F0000"))+0x08
        self.entityList: list[dict] = []
        if self.startOffset == 0: return
        for i in range(self.startOffset, self.endOffset, 0x08):
            self.entityList.append({
                "x": int.from_bytes(self.data[i:i+4], byteorder='little'),
                "y": int.from_bytes(self.data[i+4:i+6], byteorder='little'),
                "slot": int.from_bytes(self.data[i+6:i+8], byteorder='little')})

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
    def __init__(self, data: bytes, compressed: bool):
        if compressed:
            self.data = ndspy.lz10.decompress(data)
        else:
            self.data = data
            
        self.palHeaderCount = int.from_bytes(self.data[0x00:0x04], 'little')
        assert self.palHeaderCount < 0xFF
        self.paletteHeaders: list[PaletteHeader] = []
        self.paletteOffsets = []
        for i in range(self.palHeaderCount):
            self.paletteOffsets.append(int.from_bytes(self.data[0x04+i*0x04:0x08+i*0x04], 'little'))
        for i in range(self.palHeaderCount):
            self.paletteHeaders.append(PaletteHeader(self.data[self.paletteOffsets[i]:self.paletteOffsets[i+1] if i+1<self.palHeaderCount else -1]))
        

    def toBytes(self):
        # convert properties back to bytes
        return ndspy.lz10.compress(self.data)
    
class PaletteHeader:
    def __init__(self, data: bytes):
        self.data = data
        self.palCount = int.from_bytes(self.data[0x00:0x04], 'little')
        self.palettes: list[int, int] = []
        for i in range(self.palCount):
            self.palettes.append([int.from_bytes(self.data[0x04+i*0x08:i*0x08+0x08], 'little'), # ID?
                                  int.from_bytes(self.data[0x08+i*0x08:i*0x08+0x0C], 'little')]) # Pointer
        self.palEnd = [int.from_bytes(self.data[0x04+self.palCount*0x08:self.palCount*0x08+0x08], 'little'),
                       int.from_bytes(self.data[0x08+self.palCount*0x08:self.palCount*0x08+0x0C], 'little')]