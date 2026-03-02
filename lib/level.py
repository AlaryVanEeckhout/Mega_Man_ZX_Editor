
from lib import common
import ndspy.lz10

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192

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
    def __init__(self, data: bytes, baseRAMAddress: int, structRAMAddress: int, entitySlotRAMAddress: int, entityCoordRAMAddress: int, entitynamedict: dict[str, dict]):
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
        self.screenLayout0_address = self.getFileAddress(self.screenLayout0_RAMAddress)
        self.screenLayout1_RAMAddress = int.from_bytes(self.data[self.struct_address+0x14:self.struct_address+0x18], byteorder='little')
        self.screenLayout1_address = self.getFileAddress(self.screenLayout1_RAMAddress)
        self.screenLayout2_RAMAddress = int.from_bytes(self.data[self.struct_address+0x18:self.struct_address+0x1C], byteorder='little')
        self.screenLayout2_address = self.getFileAddress(self.screenLayout2_RAMAddress)
        self.screenLayout3_RAMAddress = int.from_bytes(self.data[self.struct_address+0x1C:self.struct_address+0x20], byteorder='little')
        self.screenLayout3_address = self.getFileAddress(self.screenLayout3_RAMAddress)
        self.screenLayout_radar_RAMAddress = int.from_bytes(self.data[self.struct_address+0x20:self.struct_address+0x24], byteorder='little')
        self.screenLayout_radar_address = self.getFileAddress(self.screenLayout_radar_RAMAddress)
        self.map_tilesetOffset_RAMAddress = int.from_bytes(self.data[self.struct_address+0xC8:self.struct_address+0xCC], byteorder='little') # maybe?
        self.map_tilesetOffset_address = self.getFileAddress(self.map_tilesetOffset_RAMAddress)
        self.unk_RAMAddress = int.from_bytes(self.data[self.struct_address+0xEC:self.struct_address+0xF0], byteorder='little')
        self.map_behavior_RAMAddress = int.from_bytes(self.data[self.struct_address+0xF0:self.struct_address+0xF4], byteorder='little') # maybe?
        self.map_behavior_address = self.getFileAddress(self.map_behavior_RAMAddress)
        self.screenLayout_camera_RAMAddress = int.from_bytes(self.data[self.struct_address+0xF4:self.struct_address+0xF8], byteorder='little')
        self.screenLayout_camera_address = self.getFileAddress(self.screenLayout_camera_RAMAddress)

        print(f"0x{self.screenLayout0_RAMAddress:08X}: layout0")
        self.screenLayout0 = ScreenLayout(self.data, self.screenLayout0_address)
        print(f"0x{self.screenLayout1_RAMAddress:08X}: layout1")
        self.screenLayout1 = ScreenLayout(self.data, self.screenLayout1_address)
        print(f"0x{self.screenLayout2_RAMAddress:08X}: layout2")
        self.screenLayout2 = ScreenLayout(self.data, self.screenLayout2_address)
        print(f"0x{self.screenLayout3_RAMAddress:08X}: layout3")
        self.screenLayout3 = ScreenLayout(self.data, self.screenLayout3_address)
        print(f"0x{self.map_tilesetOffset_RAMAddress:08X}: layout radar")
        self.screenLayout_radar = ScreenLayout(self.data, self.screenLayout_radar_address)
        print(f"0x{self.map_tilesetOffset_RAMAddress:08X}: map tilesetOffset (?)")
        self.map_tilesetOffset = ScreenMap(self.data, self.map_tilesetOffset_address)
        print(f"0x{self.map_behavior_RAMAddress:08X}: map behavior (?)")
        self.map_behavior = ScreenMap(self.data, self.map_behavior_address)
        print(f"0x{self.screenLayout_camera_RAMAddress:08X}: layout camera")
        self.screenLayout_camera = ScreenLayout(self.data, self.screenLayout_camera_address, loadReal=False)

        print("Entities")
        print(f"0x{self.entityCoord_RAMAddress:08X}")

        self.entities = Entities(self.data, self.entitySlot_address, self.entityCoord_address, entitynamedict)

    def getFileAddress(self, RAMAddress: int):
        return RAMAddress - self.RAMAddress
    
    def toBytes(self):
        # Layouts
        screenLayout0_bin = self.screenLayout0.toBytes()
        self.data[self.screenLayout0_address:self.screenLayout0_address+len(screenLayout0_bin)] = screenLayout0_bin
        screenLayout1_bin = self.screenLayout1.toBytes()
        self.data[self.screenLayout1_address:self.screenLayout1_address+len(screenLayout1_bin)] = screenLayout1_bin
        screenLayout2_bin = self.screenLayout2.toBytes()
        self.data[self.screenLayout2_address:self.screenLayout2_address+len(screenLayout2_bin)] = screenLayout2_bin
        screenLayout3_bin = self.screenLayout3.toBytes()
        self.data[self.screenLayout3_address:self.screenLayout3_address+len(screenLayout3_bin)] = screenLayout3_bin
        screenLayout_radar_bin = self.screenLayout_radar.toBytes()
        self.data[self.screenLayout_radar_address:self.screenLayout_radar_address+len(screenLayout_radar_bin)] = screenLayout_radar_bin
        screenLayout_camera_bin = self.screenLayout_camera.toBytes()
        self.data[self.screenLayout_camera_address:self.screenLayout_camera_address+len(screenLayout_camera_bin)] = screenLayout_camera_bin
        map_tilesetOffset_bin = self.map_tilesetOffset.toBytes()
        self.data[self.map_tilesetOffset_address:self.map_tilesetOffset_address+len(map_tilesetOffset_bin)] = map_tilesetOffset_bin
        map_behavior_bin = self.map_behavior.toBytes()
        self.data[self.map_behavior_address:self.map_behavior_address+len(map_behavior_bin)] = map_behavior_bin
        # Entities
        coords_bin = self.entities.coords.toBytes()
        self.data[self.entityCoord_address:self.entityCoord_address+len(coords_bin)] = coords_bin
        slots_bin = self.entities.slots.toBytes()
        self.data[self.entitySlot_address:self.entitySlot_address+len(slots_bin)] = slots_bin
        return self.data
        

class ScreenLayout:
    def __init__(self, data: bytes, address: int, loadReal: bool=True):
        self.realWidth = int.from_bytes(data[address:address+0x01], byteorder='little') # width used to load screens with correct alignment
        self.skip = int.from_bytes(data[address+0x01:address+0x02], byteorder='little') # idk
        self.width = int.from_bytes(data[address+0x02:address+0x03], byteorder='little') # width of used portion of layout
        self.height = int.from_bytes(data[address+0x03:address+0x04], byteorder='little')
        self.size_header = 0x04
        self.size_data = self.width*self.height
        self.size = self.size_header+self.size_data
        self.data = data[address:address+self.size]
        loadWidth = self.realWidth if loadReal else self.width
        self.layout: list[list[int]] = []
        layoutRow = []
        i_skip = 0
        print(self.realWidth, self.skip, self.width, self.height)

        for i in range(self.size_header, self.size):
            index = i + i_skip
            layoutRow.append(int.from_bytes(self.data[index:index+0x01], byteorder='little'))
            if len(layoutRow) == loadWidth:
                self.layout.append(layoutRow.copy())
                layoutRow.clear()
                i_skip += self.width - loadWidth
        print([[f"{screenID:02X}" for screenID in row] for row in self.layout])
    
    def toBytes(self):
        return self.data

class ScreenMap:
    def __init__(self, data: bytes, address: int, loadReal: bool=True):
        self.realWidth = int.from_bytes(data[address:address+0x02], byteorder='little') # width used to define effective screen space
        self.skip = int.from_bytes(data[address+0x02:address+0x04], byteorder='little') # idk
        self.width = int.from_bytes(data[address+0x04:address+0x06], byteorder='little') # width used to load all screens
        self.height = int.from_bytes(data[address+0x06:address+0x08], byteorder='little')
        self.size_header = 0x08
        self.size_data = self.width*self.height*0x02
        self.size = self.size_header+self.size_data
        self.data = data[address:address+self.size]
        loadWidth = self.realWidth if loadReal else self.width
        self.layout: list[list[int]] = []
        layoutRow = []
        i_skip = 0
        print(self.realWidth, self.skip, self.width, self.height)

        for i in range(self.size_header, self.size, 0x02):
            index = i + i_skip
            layoutRow.append(int.from_bytes(self.data[index:index+0x02], byteorder='little'))
            if len(layoutRow) == loadWidth:
                self.layout.append(layoutRow.copy())
                layoutRow.clear()
                i_skip += self.width - loadWidth
        print([[f"{screenID:04X}" for screenID in row] for row in self.layout])
    
    def toBytes(self):
        return self.data

# for convenience
class Entities:
    def __init__(self, data: bytes, entitySlotaddress: int, entityCoordAddress: int, namedict: dict[str, dict]):
        self.data = data
        if entitySlotaddress > 0:
            self.slots = EntitySlots(self.data, entitySlotaddress, namedict)
            print(self.slots.entityList)
        if entityCoordAddress > 0:
            self.coords = EntityCoordinates(self.data, entityCoordAddress)
            print(self.coords.entityList)

# EntityTemplate of rmz3 decomp
class EntitySlots:
    def __init__(self, data: bytes, address: int, namedict: dict[str, dict]):
        self.data = data
        self.entityList: list[dict] = []
        self.nameList: list[dict] = []
        index = address
        while True:
            entity_data = self.data[index:index+0x0C]
            if len(entity_data) != 0x0C or entity_data[11] != 0x00: # idk if this is the right way to see if structure ends
                #print(entity_data.hex())
                break
            dict_current = namedict
            dict_previous = None
            param_list = []
            param_size = 4 # how many levels of dicts there are
            for i in range(1, param_size+1):
                if (not len(param_list) or (len(param_list) and not param_list[i-2].startswith("0x"))) and entity_data[i] in dict_current:
                    param_list.append(dict_current[entity_data[i]][0])
                elif dict_previous is not None and None in dict_previous.keys() and entity_data[i] in dict_previous[None][1]: # search for wildcard info
                    param_list.append(dict_previous[None][1][entity_data[i]][0])
                else: # no matches found
                    param_list.append(f"0x{entity_data[i]:02X}")
                if len(param_list) == param_size: break
                dict_previous = dict_current
                try:
                    dict_current = dict_current[entity_data[i]][1] # go to dict nested inside
                except KeyError:
                    dict_current = {}
            #kind = dict_current[entity_data[1]][0] if entity_data[1] in dict_current else f"0x{entity_data[1]:02X}"
            #dict_current = dict_current[entity_data[1]][1]
            #subkind = dict_current[entity_data[2]][0] if not kind.startswith("0x") and entity_data[2] in dict_current else f"0x{entity_data[2]:02X}"
            #dict_current = dict_current[entity_data[2]][1]
            #role = dict_current[entity_data[3]][0] if not id.startswith("0x") and entity_data[3] in dict_current else f"0x{entity_data[3]:02X}"
            self.entityList.append({
                "attr": entity_data[0], # might be some kind of bitmask: 0x02 for collectibles(?), 0x40 is used sometimes...
                "kind": entity_data[1],
                "subkind": entity_data[2],
                "role": entity_data[3],
                "modifier": entity_data[4],
                "unk5": entity_data[5],
                "unk6": entity_data[6], # a count for something
                "unk7": entity_data[7],
                "unk8": entity_data[8], # 0x00 or 0xFF
                "unk9": entity_data[9],
                "unkA": entity_data[10],
                "unkB": entity_data[11],
            })
            self.nameList.append({
                "attr": f"0x{entity_data[0]:02X}", # might be some kind of bitmask: 0x02 for collectibles(?), 0x40 is used sometimes...
                "kind": param_list[0],
                "subkind": param_list[1],
                "role": param_list[2],
                "modifier": param_list[3],
                "unk5": f"0x{entity_data[5]:02X}",
                "unk6": f"0x{entity_data[6]:02X}", # a count for something
                "unk7": f"0x{entity_data[7]:02X}",
                "unk8": f"0x{entity_data[8]:02X}", # 0x00 or 0xFF
                "unk9": f"0x{entity_data[9]:02X}",
                "unkA": f"0x{entity_data[10]:02X}",
                "unkB": f"0x{entity_data[11]:02X}",
            })
            index += 0x0C
    
    def toBytes(self):
        data = bytes()
        for entity in self.entityList:
            for key in entity:
                val = entity[key]
                data += int.to_bytes(val, 1, byteorder='little')
        return data

# EntityTemplateCoord of rmz3 decomp
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
    
    def toBytes(self):
        data = bytes()
        for entity in self.entityList:
            #data += bytes.fromhex(hex(entity["x"]).removeprefix("0x")+hex(entity["y"]).removeprefix("0x")+hex(entity["slot"]).removeprefix("0x"))
            for key in entity:
                val = entity[key]
                data += int.to_bytes(val, 4 if key=="x" else 2, byteorder='little')
        return data

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