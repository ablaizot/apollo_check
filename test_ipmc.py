import subprocess

class IPMC:
    def __init__(self, ip, ipmb_0_address, firmware_commit):
        self.ip = ip
        self.ipmb_0_address = ipmb_0_address
        self.firmware_commit = firmware_commit

    def getFirmware(self):
        return self.firmware_commit

print(subprocess.run(["/home/ablaizot/test_ipmc.sh"],shell=True))

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

print("IP:", ipmc.ip)
print("IPMB-0 Address:", ipmc.ipmb_0_address)
print("Firmware Commit:", ipmc.firmware_commit)

print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " fru >> logs_ipmc"],shell=True))
print(subprocess.run(["ipmitool -H 192.168.10.172 -P \"\" -t " + ipmc.ipmb_0_address + " sensor >> logs_ipmc"],shell=True))

print(check_firmware(read_logs("logs_ipmc"),ipmc))
