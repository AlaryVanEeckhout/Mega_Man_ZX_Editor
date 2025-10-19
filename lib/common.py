class File:
    def __init__(self, data: bytes):
        self.data = data
        self.entryCount = int.from_bytes(self.data[0x00:0x04], byteorder='little') # entries start at 0x04 and exclude file size
        self.address_list: list[list[int]] = []
        self.fileSize = int.from_bytes(self.data[0x04+self.entryCount*4:self.entryCount*4+0x08], byteorder='little')
        for index in range(self.entryCount): 
            offset = 0x04+index*0x04 # 4 bytes per entry
            self.address_list.append([int.from_bytes(self.data[offset:offset+0x03], byteorder="little"), #rom offset
                                      int.from_bytes(self.data[offset+0x03:offset+0x04], byteorder="little")]) # =0x80 if lz10 compressed, else 0
            assert self.address_list[index][0] < self.fileSize
            if index > 0:
                assert self.address_list[index][0] >= self.address_list[index-1][0]
        self.header_size = self.address_list[0][0] if self.entryCount>0 else 0x04

    def headerToBytes(self):
        data = bytearray()
        data += int.to_bytes(self.entryCount, 0x04, 'little')
        for pointer in self.address_list:
            data += int.to_bytes(pointer[0]|(pointer[1]<<0x18), 0x04, 'little')
        data += int.to_bytes(self.fileSize, 0x04, 'little')
        return bytes(data)