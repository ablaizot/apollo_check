import socket
import subprocess
import time
import ipmc_def
import apollo_def

def main():
   

    [host_list, out_path] = apollo_def.validate_connections()

    

    for HOST in host_list:
        try:
            
            # Set the ssh command with timeout of 10 seconds
            ssh_command = f"ssh -o ConnectTimeout=10 cms@{HOST} systemctl --failed"
            print(subprocess.run([ssh_command],shell=True))
            # Use subprocess to run the command
            #ssh_proc = subprocess.Popen(ssh_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
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
