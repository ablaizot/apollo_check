import socket
import subprocess
import time
import ipmc_scripts

class IPMC:
    def __init__(self, ip, ipmb_0_address, firmware_commit):
        self.ip = ip
        self.ipmb_0_address = ipmb_0_address
        self.firmware_commit = firmware_commit

    def getFirmware(self):
        return self.firmware_commit

#print(subprocess.run(["/home/ablaizot/test_ipmc.sh"],shell=True))

def extract_ipmc(file_contents):
    lines = file_contents.split("\n")
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
    return IPMC(ip, address, firmware)

def read_logs(file_path):
    with open(file_path) as f:
        file_contents = f.read()
    return file_contents

def check_firmware(file_contents,IPMC):
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

ipmc = extract_ipmc(read_logs("logs_ipmc"))

def main():
    args = ipmc_scripts.parse_cli()

    board = f'SM{args.board_number}'

    # Check board serial
    if board not in ipmc_scripts.SM_TO_IPMC:
        raise ValueError(f'IPMC cannot be found for Apollo: {board}')

      # IP address of the IPMC
    HOST = ipmc_scripts.SM_TO_IPMC[board]

    # Retrieve and validate the configuration
    config = ipmc_scripts.read_config(args.config_path)
    ipmc_scripts.validate_config(config)
    
    commands = ipmc_scripts.get_commands(config)

        # Timeout value (s) for socket connection
    timeout = 5

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Make the connection
        s.connect((HOST, ipmc_scripts.PORT))
        s.settimeout(timeout)
        
        print(f'\n> Connection established to: {HOST}:{ipmc_scripts.PORT}')
        print(f'> Timeout set to: {timeout} s')
        print(f'> Executing update commands...\n')

        # Execute the commands and read back data
        for command in commands:
            print(f'>> {command}', end='   ')
            try:
                output = ipmc_scripts.write_command_and_read_output(s, command)
                print('-> OK')
            except socket.timeout:
                print('-> Command timed out, skipping.')
                continue
            
            time.sleep(0.5)
        
        # Do a final read of the EEPROM before exiting
        print('\nCommands are done. EEPROM reads as:')
        out = ipmc_scripts.write_command_and_read_output(s, "eepromrd\r\n")
        print(out)

        # Validate the command output
        ipmc_scripts.validate_command_output(output, config)
    print(out)
    print(output)
    print(config)

if __name__ == '__main__':   
    main()

print("IP:", ipmc.ip)
print("IPMB-0 Address:", ipmc.ipmb_0_address)
print("Firmware Commit:", ipmc.firmware_commit)

print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " fru >> logs_ipmc"],shell=True))
print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " sensor >> logs_ipmc"],shell=True))

print(check_firmware(read_logs("logs_ipmc"),ipmc))
