#!/usr/bin/env python3

import os
import sys
import time
import yaml
import socket
import argparse
import xml

# Check Python version, need at least 3.6
valid_python = sys.version_info.major >= 3 and sys.version_info.minor >= 6 
assert valid_python, "You need Python version >=3.6 to run this script!"

# The port for the telnet service on the IPMC
PORT = 23


#define IPMC object with fields gathered from telnetting to it and ipmi tool
class IPMC:
    def __init__(self, ip, hw, ipmb_0_address, firmware_commit, firmware_commit_check,ipmi_time):
        self.ip = ip
        self.hw = hw
        self.ipmb_0_address = ipmb_0_address
        self.firmware_commit = firmware_commit
        self.firmware_commit_check = firmware_commit_check
        self.ipmi_time = ipmi_time

    def getFirmware(self):
        return self.firmware_commit

    def getipmb_0_address(self):
        return self.ipmb_0_address

    #for yaml config
    def to_dict(self):
        return {
            'hw': self.hw,
            'Ipmi Time':self.ipmi_time,
            'IPMB 0 address': self.ipmb_0_address,
            'Firmware commit check': self.firmware_commit_check,
            'Firmware commit': self.firmware_commit,
            'IP': self.ip,
        }

def parse_cli():
    parser = argparse.ArgumentParser()
    #either board number or ip needs to be provided
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b','--board_number', type=str, help='The serial number of the Apollo SM.',nargs='+')
    group.add_argument('-ip','--ipmc_ip',type=str,help='IP address of IPMC',nargs='+')

    parser.add_argument('-c', '--config_path', default='config/ipmc_ip_config.yaml', help='Path to the IPMC IP config file.')
    parser.add_argument('-o', '--out_path', default='config/ipmc_out.yaml', help='Path to the IPMC out file.')

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

    SM_TO_IPMC = read_config(args.config_path)


    ipmc_ip_list = []
    board_list = []

    
    if args.ipmc_ip:
        for i in args.ipmc_ip:
            if i not in SM_TO_IPMC:
                raise ValueError(f'IPMC cannot be found for IP: {i}')
            ipmc_ip_list.append(f'{i}')

    elif args.board_number:
        for i in args.board_number:
            if i not in SM_TO_IPMC:
                raise ValueError(f'IPMC cannot be found for Apollo: {i}')
            board_list.append(f'SM{i}')
    else:
        raise ValueError('No Argument')

    return ipmc_ip_list, board_list, args.out_path


def extract_ipmc(file_contents):
    #makes ipmc object from information from telnet
    lines = file_contents.split("\n")
    hw = None
    ip = None
    address = None
    firmware = None
    for line in lines:
        if "IP Addr:" in line:
            ip = line.split("IP Addr:")[1].strip()
        elif "IPMB-0 Addr:" in line:
            address = line.split("IPMB-0 Addr:")[1].strip()
        elif "Firmware commit:" in line:
            firmware = line.split("Firmware commit:")[1].strip()
        elif "hw           =" in line:
            hw = line.split("hw           =")[1].strip()
    return IPMC(ip, hw, address, firmware,None,None)

def read_logs(file_path):
    with open(file_path) as f:
        file_contents = f.read()
    return file_contents

def check_firmware(file_contents,IPMC):
    #Checks if the telnet firmware version is the same as the one given by ipmitool
    lines = file_contents.split("\n")
    check = None
    firmware = None
    for line in lines:
        if "Product Asset Tag     :" in line:
            firmware = line.split("Product Asset Tag     :")[1].strip()

    if firmware.lower() == IPMC.getFirmware():
        check = True
    else:
        check = False
    return check

def write_ipmc_to_yaml(ipmc_list, filepath):
    with open(filepath, 'w') as f:
        yaml.dump([ipmc.to_dict() for ipmc in ipmc_list], f)
