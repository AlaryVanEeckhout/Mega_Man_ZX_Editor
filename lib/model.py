from lib import common
# https://problemkaputt.de/gbatek-ds-3d-i-o-map.htm
COMMAND_SIZES = { # in word count
    0x00 : 0, # NOP
    0x10 : 1,
    0x11 : 0,
    0x12 : 1,
    0x13 : 1,
    0x14 : 1,
    0x15 : 0,
    0x16 : 16,
    0x17 : 12,
    0x18 : 16,
    0x19 : 12,
    0x1A : 9,
    0x1B : 3,
    0x1C : 3,
    0x20 : 1, # COLOR
    0x21 : 1, # NORMAL
    0x22 : 1, # TEXCOORD
    0x23 : 2, # XYZ COORDINATES
    0x24 : 1,
    0x25 : 1,
    0x26 : 1,
    0x27 : 1,
    0x28 : 1,
    0x29 : 1,
    0x2A : 1,
    0x2B : 1,
    0x30 : 1,
    0x31 : 1,
    0x32 : 1,
    0x33 : 1,
    0x34 : 32,
    0x40 : 1, # BEGIN_VTXS
    0x41 : 0, # END_VTXS
    0x50 : 1,
    0x60 : 1,
    0x70 : 3,
    0x71 : 2,
    0x72 : 1
}

class File(common.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ModelHeader:
    def __init__(self, data: bytes):
        self.SUBHEADERSIZE = 0x4C
        self.data = data
        self.nameCount = int.from_bytes(self.data[0:0x04], 'little')
        self.geometries: list[GeometryHeader] = []
        for i in range(0x04, 0x04+self.nameCount*self.SUBHEADERSIZE, self.SUBHEADERSIZE):
            self.geometries.append(GeometryHeader(self.data[i:i+self.SUBHEADERSIZE]))

class GeometryHeader: # to complete
    def __init__(self, data: bytes):
        self.STRINGSIZE = 0x40
        self.data = data
        self.name = self.data[0:self.STRINGSIZE].decode().replace("\x00", "")
        self.textureID = int.from_bytes(self.data[self.STRINGSIZE:self.STRINGSIZE+0x04],'little')
        self.geometry_offset = int.from_bytes(self.data[self.STRINGSIZE+0x04:self.STRINGSIZE+0x08],'little')
        self.geometry_size = int.from_bytes(self.data[self.STRINGSIZE+0x08:self.STRINGSIZE+0x0C],'little')

class Geometry:
    def __init__(self, data: bytes):
        self.data = data
        self.commands = []
        self.params = []
        i = 0
        while i < len(self.data):
            commands = self.data[i:i+0x04]
            i += 4
            self.commands += commands
            for c in commands:
                param = self.data[i:i+COMMAND_SIZES[c]*4]
                i += COMMAND_SIZES[c]*4
                self.params.append(param)

