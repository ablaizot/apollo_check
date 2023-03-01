import socket
import subprocess
import time
import apollo_def

def main():
   

    [host_list, out_path] = apollo_def.validate_connections()

    commands = ['systemctl --failed','BUTool.exe -a','readconvert SLAVE_I2C.S8.IPMC_IP','exit']

    apollo_list = []
    #Connects to each apollo and sends set of commands
    for HOST in host_list:
        out = None
        error = None
        try:

            ssh_cmd = ['ssh', f'cms@{HOST}']
            
            ssh_session = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            #Writing command by command
            for command in commands:
                ssh_session.stdin.write(command.encode())
                ssh_session.stdin.write(b'\n')
            ssh_session.stdin.close()

            for line in ssh_session.stdout:
                out = line.decode().rstrip()
                print(out)
            for line in ssh_session.stderr:
                error = line.decode().rstrip()
                print(error)

            ssh_session.wait()


        except subprocess.TimeoutExpired:
            print("SSH connection timed out.")
        except Exception as e:
            print("An error occurred:", e)

        print(error)
        apollo = apollo_def.extract_apollo(HOST,out)
        apollo_list.append(apollo)
        print("IP:", apollo.ip)
        print("Name:", apollo.name)
        print("IPMC:", apollo.ipmc)
        print("Firmware Commit:", apollo.firmware_commit)

if __name__ == '__main__':   
    main()
