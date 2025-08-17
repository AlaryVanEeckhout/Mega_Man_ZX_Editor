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
            print(self.palettes[i].colors)
            

    def toBytes(self):
        data = bytearray()
        #data += int.to_bytes(self.offset_anims)
        return data
    
class PaletteAnimInfo:
    def __init__(self, data: bytes):
        self.data = data
        self.frameCount = int.from_bytes(self.data[0x00:0x01])
        self.colorSlot0 = int.from_bytes(self.data[0x01:0x02])
        self.colorSlot1 = int.from_bytes(self.data[0x02:0x03])
        self.colors: list[list[int]] = []
        for i in range(0x04, len(self.data), 0x04):
            self.colors.append(datconv.BGR15_to_ARGB32(self.data[i:i+0x04]))