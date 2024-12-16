class VX():
    def __init__(self, data: bytes):
        self.signature = data[0x00:0x04]
        self.frame_count = int.from_bytes(data[0x04:0x08], "little")
        self.frame_width = int.from_bytes(data[0x08:0x0C], "little")
        self.frame_height = int.from_bytes(data[0x0C:0x10], "little")
        self.frame_rate = int.from_bytes(data[0x10:0x14], "little") / 0x10000  # convert from 16.16 to fraction
        self.quantiser = int.from_bytes(data[0x14:0x18], "little")
        self.audio_sampleRate = int.from_bytes(data[0x18:0x1C], "little")
        self.audio_streamCount = int.from_bytes(data[0x1C:0x20], "little")
        self.frame_sizeMax = int.from_bytes(data[0x20:0x24], "little") # size of data
        self.audio_extraDataOffset = int.from_bytes(data[0x24:0x28], "little")
        self.seekTable_offset = int.from_bytes(data[0x28:0x2C], "little")
        self.seekTable_entryCount = int.from_bytes(data[0x2C:0x30], "little")

    def generateFrames():
        pass

    def saveFromFrames():
        pass