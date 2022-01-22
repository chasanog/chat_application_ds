import socket
import struct

import server_data
import ports
import multicast_data
import pickle
from time import sleep

import pickle

# global variable definitions for multicast sender
multicastAddress = (multicast_data.MCAST_GRP, multicast_data.MCAST_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)



# will be sent when a new connection applied and established
def requestToMulticast():
    sleep(1)
    message = pickle.dumps([multicast_data.SERVER_LIST, multicast_data.LEADER])
    sock.sendto(message, multicastAddress)
    print(f'\nMulticast sending data to receivers from {server_data.SERVER_IP} to {multicastAddress}')

    try:
        sock.recvfrom(1024)
        if multicast_data.LEADER == server_data.SERVER_IP:
            print(f'{sock.getsockname()[0]}: Sending updates to all servers\n')
        return True
    except socket.timeout:
        print(f'{server_data.SERVER_IP}: Currently no receiver reachable')
        return False

# sent by clients join requests
def requestToJoinChat():

    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicastAddress)
    sleep(0.5)
    try:
        data, address = sock.recvfrom(1024)
        multicast_data.LEADER = pickle.loads(data)[0]
        return True
    except socket.timeout:
        return False