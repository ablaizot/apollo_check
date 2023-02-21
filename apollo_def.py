import argparse

class apollo:
    def __init__(self, ip, name, ipmc,firmware_commit):
        self.ip = ip    
        self.name = name
        self.ipmc = ipmc
        self.firmware_commit = firmware_commit

    def getFirmware(self):
        return self.firmware_commit

def parse_cli():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b','--board_number', type=int, help='The serial number of the Apollo SM.',nargs='?')
    group.add_argument('-c', '--config-path', default='config/ipmc_config.yaml', help='Path to the IPMC config file.')
    parser.add_argument('-ip','--apollo_ip',type=str,help='IP address of apollo',nargs='?')
    args = parser.parse_args()
    return args