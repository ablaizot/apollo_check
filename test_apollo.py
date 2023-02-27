import socket
import subprocess
import time
import ipmc_def
import apollo_def

def main():
   

    [host_list, out_path] = apollo_def.validate_connections()

    commands = ['ls -al', 'systemctl --failed','dmesg']

    for HOST in host_list:
        try:
            
            # Set the ssh command with timeout of 10 seconds
            ssh_cmd = ['ssh', f'cms@{HOST}']
            
            #print(subprocess.run([ssh_command],shell=True))
            # Use subprocess to run the command
            #ssh_proc = subprocess.Popen(ssh_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ssh_session = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for command in commands:
                ssh_session.stdin.write(command.encode())
                ssh_session.stdin.write(b'\n')
            ssh_session.stdin.close()
            for line in ssh_session.stdout:
                print(line.decode().rstrip())
            for line in ssh_session.stderr:
                print(line.decode().rstrip())
            ssh_session.wait()
            # Wait for the command to finish or timeout
            #stdout, stderr = ssh_proc.communicate(timeout=10)
            
            # Print the output
            #print(stdout.decode())
            #print(stderr.decode())

        except subprocess.TimeoutExpired:
            print("SSH connection timed out.")
        except Exception as e:
            print("An error occurred:", e)


if __name__ == '__main__':   
    main()
