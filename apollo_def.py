import argparse
import os
import socket
import yaml

class APOLLO:
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
    group.add_argument('-b','--board_number', type=str, help='The serial number of the Apollo SM.',nargs='+')
    group.add_argument('-ip','--apollo_ip',type=str,help='IP address of apollo',nargs='+')

    parser.add_argument('-c', '--config-path', default='config/apollo_ip_config.yaml', help='Path to the IPMC config file.')

    parser.add_argument('-o', '--out_path', default='config/apollo_out.yaml', help='Path to the IPMC out file.')

    args = parser.parse_args()
    return args

def parse_out(cmd_output,field):
    out = None
    if cmd_output != None:
        lines = cmd_output.split("\n")

        for line in lines:
            if field in line:
                out = line.split(field)[1].strip()

    return out


def read_config(filepath: str):
    """Reads the YAML configuration file from the given file path."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find IPMC configuration file: {filepath}")
    
    with open(filepath, 'r') as f:
        data = yaml.load(f,Loader=yaml.FullLoader)
    
    return data 

def validate_connections():
    #Makes sure the IP is in the config
    
    args = parse_cli()

    APOLLO_IP = read_config(args.config_path)
    
    ip_list = list(APOLLO_IP.values())
    host_list = []

    if args.apollo_ip:
        for i in args.apollo_ip:
            if i not in ip_list:
                raise ValueError(f'Apollo cannot be found for IP: {i}')
            host_list.append(f'{i}')

    elif args.board_number:
        for i in args.board_number:
            if i not in APOLLO_IP:
                raise ValueError(f'Apollo cannot be found for: {i}')
            host_list.append(APOLLO_IP[i])
    else:
        raise ValueError('No Argument')

    return host_list, args.out_path

#Constructing apollo object from ssh output
def extract_apollo(host,cmd_output):
    ip = host
    name = None
    ipmc = None
    firmware_commit  = None

    ipmc = parse_out(cmd_output,"SLAVE_I2C.S8.IPMC_IP:")

    return APOLLO(ip,name,ipmc,firmware_commit)