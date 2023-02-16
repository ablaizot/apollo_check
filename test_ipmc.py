import socket
import subprocess
import time
import ipmc_scripts


def main():
    args = ipmc_scripts.parse_cli()

    board = f'SM{args.board_number}'
    ipmc_ip = {args.ipmc_ip}

    # Check board serial
    if board != None:
        if board not in ipmc_scripts.SM_TO_IPMC:
            raise ValueError(f'IPMC cannot be found for Apollo: {board}')

        # IP address of the IPMC
        HOST = ipmc_scripts.SM_TO_IPMC[board]
    elif ipmc_ip != None:
        if ipmc_ip not in ipmc_scripts.IPMC_TO_SM:
            raise ValueError(f'IPMC cannot be found for IP{ipmc_ip}')
            HOST = ipmc_ip
    else:
        raise ValueError(f'No Argument')
    # Retrieve and validate the configuration
    #config = ipmc_scripts.read_config(args.config_path)
    #ipmc_scripts.validate_config(config)
    
    #commands = ipmc_scripts.get_commands(config)

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
        
        
        try:
            output = ipmc_scripts.write_command_and_read_output(s, "info\r\n")
            print('-> OK')
        except socket.timeout:
            print('-> Command timed out, skipping.')
        
        time.sleep(0.5)
        
        # Do a final read of the EEPROM before exiting
        print('\nCommands are done. EEPROM reads as:')
        out = ipmc_scripts.write_command_and_read_output(s, "eepromrd\r\n")
        print(out)

    print(out)
    print(output)
    logs = out+output


    ipmc = ipmc_scripts.extract_ipmc(logs)
    print("IP:", ipmc.ip)
    print("IPMB-0 Address:", ipmc.ipmb_0_address)
    print("Firmware Commit:", ipmc.firmware_commit)

    print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " fru >> logs_ipmc"],shell=True))
    print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " sensor >> logs_ipmc"],shell=True))



    print(ipmc_scripts.check_firmware(ipmc_scripts.read_logs("logs_ipmc"),ipmc))


if __name__ == '__main__':   
    main()


