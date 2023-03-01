import socket
import subprocess
import time
import ipmc_def


def main():
    
    #[ipmc_ip_list, board_list, out_path] = ipmc_def.validate_connections()
        #Makes sure the IP is in the config

    args =  ipmc_def.parse_cli()

    SM_TO_IPMC =  ipmc_def.read_config(args.config_path)


    ipmc_ip_list = []
    board_list = []

    ip_list = list(SM_TO_IPMC.values())

    if args.ipmc_ip:
        for i in args.ipmc_ip:
            if i not in ip_list:
                raise ValueError(f'IPMC cannot be found for IP: {i}')
            ipmc_ip_list.append(f'{i}')

    elif args.board_number:
        for i in args.board_number:
            if i not in SM_TO_IPMC:
                raise ValueError(f'IPMC cannot be found for Apollo: {i}')
            board_list.append(f'{i}')
    else:
        raise ValueError('No Argument')

    out_path =  args.out_path

    host_list = []

    for i in board_list:
        host_list.append(SM_TO_IPMC[i])

    for i in ipmc_ip_list:
        host_list.append(i)
    

    # Retrieve and validate the configuration
    #config = ipmc_scripts.read_config(args.config_path)
    #ipmc_scripts.validate_config(config)
    
    #commands = ipmc_scripts.get_commands(config)

        # Timeout value (s) for socket connection
    timeout = 5
    ipmc_list = []
    for HOST in host_list:
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

       
        logs = out+output


        ipmc = ipmc_def.extract_ipmc(logs)
        ipmc_list.append(ipmc)
        print("IP:", ipmc.ip)
        print("IPMB-0 Address:", ipmc.ipmb_0_address)
        print("Firmware Commit:", ipmc.firmware_commit)

        #timing ipmitool
        start = time.time()

        subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " fru > logs_ipmc"],shell=True)

        end = time.time()
        ipmc.ipmi_time = (end-start)*10**3
        print("ipmitool fru time:",ipmc.ipmi_time,"ms")

        subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " sensor >> logs_ipmc"],shell=True)

        ipmc.firmware_commit_check = ipmc_def.check_firmware(ipmc_def.read_logs("logs_ipmc"),ipmc)
        print("Firmware Check:",ipmc.firmware_commit_check)

    ipmc_def.write_ipmc_to_yaml(ipmc_list,out_path)


if __name__ == '__main__':   
    main()


