from lib import common
from lib.oam import Animation
from lib import datconv

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset_anims = self.address_list[0][0]
        self.animCount = int.from_bytes(self.data[self.address_list[0][0]:self.address_list[0][0]+0x04], 'little')//0x04
        self.anims: list[Animation] = []
        self.palettes: list[PaletteAnimInfo] = []
        for i in range(self.animCount):
            self.anims.append(Animation(self.data[self.offset_anims:self.address_list[1][0]],
                                   int.from_bytes(self.data[self.offset_anims+i*0x04:self.offset_anims+i*0x04+0x04], 'little')))
            self.palettes.append(PaletteAnimInfo(self.data[
                self.address_list[i+1][0]:self.address_list[i+2][0] if i+1 < self.animCount else self.fileSize]))
            print(self.palettes[i].colorTable)
            

    def toBytes(self):
        data = bytearray()
        data += int.to_bytes(self.entryCount, 4, 'little')
        data += int.to_bytes(self.offset_anims, 4, 'little')
        anim_ptr = bytearray()
        anim_bin = bytearray()
        pal_bin = bytearray()
        for anim in self.anims:
            anim_ptr += int.to_bytes(len(anim_bin)+len(self.anims)*0x04, 4, 'little')
            anim_bin += anim.toBytes()
        anim_bin = anim_ptr + anim_bin
        for pal in self.palettes:
            data += int.to_bytes(self.offset_anims+len(anim_bin)+len(pal_bin), 4, 'little')
            pal_bin += pal.toBytes()
        data += int.to_bytes(len(data+anim_bin+pal_bin)+4, 4, 'little')
        data += anim_bin
        data += pal_bin
        #print(self.data.hex())
        #print("vs")
        #print(data.hex())
        return data
    
class PaletteAnimInfo:
    def __init__(self, data: bytes):
        self.data = data
        self.frameCount = int.from_bytes(self.data[0x00:0x01])
        self.colorSlot0 = int.from_bytes(self.data[0x01:0x02])
        self.colorSlot1 = int.from_bytes(self.data[0x02:0x03])
        self.colorTable: list[list[int]] = []
        for i in range(0x04, len(self.data), 0x04):
            self.colorTable.append(datconv.BGR15_to_ARGB32(self.data[i:i+0x04]))

    def toBytes(self):
        data = bytearray()
        data += int.to_bytes(self.frameCount, 1, 'little')
        data += int.to_bytes(self.colorSlot0, 1, 'little')
        data += int.to_bytes(self.colorSlot1, 1, 'little')
        data += bytes(1)
        for colorset in self.colorTable:
            data += datconv.ARGB32_to_BGR15(colorset)
        return data