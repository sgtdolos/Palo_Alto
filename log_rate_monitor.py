from netmiko import ConnectHandler
from getpass import getpass
import re
import time
from datetime import datetime
from signal import signal, SIGINT
 

def handler(signal_received, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        fw_connect.disconnect()
        f.close()
        exit(1)


def get_device_lograte(fw_conn):
    try:
        command = "debug log-receiver statistics | match \"Log written rate:\""
        output = fw_conn.send_command(command, use_textfsm=False)
        output = output.strip()
        temp = re.findall(r'\d+', output)
        fw_lograte = int(temp[0])
    except Exception as e:
        alert_msg = "Exception getting device baseline" + "\n" + str(e) + "\n"
        print(alert_msg)
        fw_conn.disconnect()
    return fw_lograte


timestr = time.strftime("%Y%m%d-%H%M%S")

fw = input("Enter firewall IP: ")
# Requests Username and Password from user
username = input("Username: ")

password = getpass("Password: ")

secs = input("Enter time between lograte checks (seconds): ")


out_file = "PaloFWLogRate_" + timestr + ".txt"
print(f"\nSaving results to {out_file}\n")



fw_file = fw + timestr + ".txt"

palo_ip = fw.strip()
palofw = {
    'device_type': "paloalto_panos",
    'ip': palo_ip,
    'username': username,
    'password': password,
    'session_log': fw_file,
}


if __name__ == '__main__':
    signal(SIGINT, handler)
    try:
        print(str(datetime.now()) + " -- Connecting to " + palo_ip + "\n")
        fw_connect = ConnectHandler(**palofw)
        while True:
            f = open(out_file, "a")
            rate = get_device_lograte(fw_connect)
            msg = time.strftime("%Y%m%d-%H:%M:%S") + " - Log Rate: " + str(rate)
            f.write(msg + "\n")
            print(msg)
            f.close()
            time.sleep(60)
    except Exception as e:
        alert_msg = str(datetime.now()) + " -- Exception connecting to " + palo_ip + "\n" + str(e)
        print(alert_msg)
        f = open(out_file, "a")
        f.write(alert_msg)
        exit(0)