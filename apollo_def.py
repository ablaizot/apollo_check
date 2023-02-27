import argparse
import os
import socket
import yaml

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
    group.add_argument('-b','--board_number', type=str, help='The serial number of the Apollo SM.',nargs='+')
    group.add_argument('-ip','--apollo_ip',type=str,help='IP address of apollo',nargs='+')

    parser.add_argument('-c', '--config-path', default='config/apollo_ip_config.yaml', help='Path to the IPMC config file.')

    parser.add_argument('-o', '--out_path', default='config/apollo_out.yaml', help='Path to the IPMC out file.')

    args = parser.parse_args()
    return args

def read_config(filepath: str):
    """Reads the YAML configuration file from the given file path."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find IPMC configuration file: {filepath}")
    
    with open(filepath, 'r') as f:
        data = yaml.load(f,Loader=yaml.FullLoader)
    
    return data

def write_command_and_read_output(
    sock: socket.socket, 
    command: str,
    max_size: int=2048,
    read_until: bytes=b">",
    ) -> str:
    """
    Given the socket interface, writes a command to IPMC TelNet interface 
    and returns the data echoed back.
    The maximum message size to expect is specified via the max_size argument.
    """
    counter = 0
    data = b""

    # Send the command one byte at a time
    for ch in command:
        sock.send(bytes(ch, 'utf-8'))
        # Read back the command
        _ = sock.recv(1)

    # Recieve the echoed message one byte at a time
    while counter < max_size:
        rcv = sock.recv(1)
        if rcv == read_until:
            if counter != 0:
                break
            else:
                continue
        data += rcv
        counter += 1

    # Get the leftover ">" and " " characters before exiting
    for i in range(2):
        _ = sock.recv(1)

    return data.decode('ascii')

def validate_connections():
    #Makes sure the IP is in the config
    
    args = parse_cli()

    APOLLO_IP = read_config(args.config_path)
    print(APOLLO_IP)
    host_list = []

    if args.apollo_ip:
        for i in args.apollo_ip:
            if i not in APOLLO_IP:
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

