import socket
import subprocess
import time
import ipmc_def


def main():
    args = ipmc_def.parse_cli()
    ipmc_ip = {args.ipmc_ip}

    if args.board_number !=None:
        board = f'SM{args.board_number}'
        if board != 'SMNone' or board != None:
            if board not in ipmc_def.SM_TO_IPMC:
                raise ValueError(f'IPMC cannot be found for Apollo: {board}')

            # IP address of the IPMC
            HOST = ipmc_def.SM_TO_IPMC[board]

    # Check board serial
    elif ipmc_ip != None:
        if ipmc_ip not in ipmc_def.SM_TO_IPMC:
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
        s.connect((HOST, ipmc_def.PORT))
        s.settimeout(timeout)
        
        print(f'\n> Connection established to: {HOST}:{ipmc_def.PORT}')
        print(f'> Timeout set to: {timeout} s')
        print(f'> Executing update commands...\n')

        # Execute the commands and read back data
        
        
        try:
            output = ipmc_def.write_command_and_read_output(s, "info\r\n")
            print('-> OK')
        except socket.timeout:
            print('-> Command timed out, skipping.')
        
        time.sleep(0.5)
        
        # Do a final read of the EEPROM before exiting
        print('\nCommands are done. EEPROM reads as:')
        out = ipmc_def.write_command_and_read_output(s, "eepromrd\r\n")
        print(out)

    print(out)
    print(output)
    logs = out+output


    ipmc = ipmc_def.extract_ipmc(logs)
    print("IP:", ipmc.ip)
    print("IPMB-0 Address:", ipmc_def.ipmb_0_address)
    print("Firmware Commit:", ipmc_def.firmware_commit)

    print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " fru >> logs_ipmc"],shell=True))
    print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " sensor >> logs_ipmc"],shell=True))



    print(ipmc_def.check_firmware(ipmc_def.read_logs("logs_ipmc"),ipmc))


if __name__ == '__main__':   
    main()


