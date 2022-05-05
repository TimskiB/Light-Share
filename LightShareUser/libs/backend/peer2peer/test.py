import scapy.all as scapy
import argparse
import socket
import threading


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='target', help='Target IP Address/Adresses')
    options = parser.parse_args()

    # Check for errors i.e if the user does not specify the target IP Address
    # Quit the program if the argument is missing
    # While quitting also display an error message
    if not options.target:
        # Code to handle if interface is not specified
        parser.error("[-] Please specify an IP Address or Addresses, use --help for more info.")
    return options


def scan(ip):
    arp_req_frame = scapy.ARP(pdst=ip)

    broadcast_ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout=1, verbose=False)[0]
    result = []
    for i in range(0, len(answered_list)):
        client_dict = {"ip": answered_list[i][1].psrc, "mac": answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result


def display_result(result):
    print("-----------------------------------\nIP Address\tMAC Address\n-----------------------------------")
    local_addresses = []
    for i in result:
        print("{}\t{}".format(i["ip"], i["mac"]))
        local_addresses.append(i["ip"])
    print(f"I have {len(local_addresses)} local addresses")
    return local_addresses


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# options = get_args()
# my_ip = ".".join(get_my_ip().split(".")[:3]) + ".1/24"
# print(my_ip)
#target = "10.100.102.1/24"
target = ".".join(get_my_ip().split(".")[:3]) + ".1/24"
scanned_output = scan(target)
addrs = display_result(scanned_output)


def port_scanner(port, target):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target, port))
        print(f"Port {port} is open in {target}")
    except:
        pass


for addr in addrs:

    target = addr  # scan local host

    for port in range(12340, 12350):
        thread = threading.Thread(target=port_scanner, args=[port, target, ])
        thread.start()
