
class apollo:
    def __init__(self, ip, name, ipmc,):
        self.ip = ip    
        self.name = name
        self.ipmc = ipmc
        self.firmware_commit = firmware_commit

    def getFirmware(self):
        return self.firmware_commit