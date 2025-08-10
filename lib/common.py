class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(self.data[0x00:0x04], byteorder='little') # entries start at 0x04
        self.address_list = []
        self.fileSize = int.from_bytes(self.data[0x04+self.entryCount*4:self.entryCount*4+0x08], byteorder='little')
        for index in range(self.entryCount): 
            self.address_list.append(int.from_bytes(self.data[0x04+index*4:index*4+0x08], byteorder="little")) # 4 bytes per entry
            assert self.address_list[index] & 0xFFFFFF < self.fileSize
            if index > 0:
                assert self.address_list[index] & 0xFFFFFF >= self.address_list[index-1] & 0xFFFFFF