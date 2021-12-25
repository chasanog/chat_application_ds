import socket
import struct

import server_data
import ports
import multicast_data
import pickle
from time import sleep

import pickle


multicastAddress = (multicast_data.MCAST_GRP, multicast_data.MCAST_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
ttl = struct.pack('b', 1)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)




def requestToMulticast():
    sleep(1)
    message = pickle.dumps([multicast_data.SERVER_LIST, multicast_data.LEADER])
    sock.sendto(message, multicastAddress)
    print(f'\n [MULTICAST SENDER {server_data.SERVER_IP}] Sending data to Multicast Receivers {multicastAddress}')

    try:
        sock.recvfrom(1024)

        if multicast_data.LEADER == sock.getsockname()[0]:
            print(f'[MULTICAST SENDER {sock.getsockname()[0]}] All Servers have been updated \n')
        return True
    except socket.timeout:
        print(f'[MULTICAST SENDER {server_data.SERVER_IP}] Multicast Receiver not detected')
        return False