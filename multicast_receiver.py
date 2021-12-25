import pickle
import socket
import struct

import multicast_data
import ports
import server_data

multicastIP = multicast_data.MCAST_GRP
serverAddress = ('', ports.MULTICAST)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def start_receiver():
    sock.bind(serverAddress)

    #WTH
    group = socket.inet_aton(multicastIP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n [MULTICAST RECEIVER {server_data.SERVER_IP}] Starting UDP Socket and listening on Port {ports.MULTICAST}')

    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] Received data from {address} \n')

            if len(pickle.loads(data)[0] == 0):
                multicast_data.SERVER_LIST.append(address[0]) if address[0] not in multicast_data.SERVER_LIST else multicast_data.SERVER_LIST
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] Closing UDP Socket')