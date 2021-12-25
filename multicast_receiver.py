import pickle
import socket
import struct

import multicast_data
import ports
import server_data

multicastIP = multicast_data.MCAST_GRP
serverAddress = ('', multicast_data.MCAST_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def start_receiver():
    sock.bind(serverAddress)

    #WTH
    group = socket.inet_aton(multicastIP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {server_data.SERVER_IP}] Starting UDP Socket and listening on Port {multicast_data.MCAST_PORT}')

    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] Received data from {address} \n')

            if multicast_data.LEADER == server_data.SERVER_IP and pickle.loads(data) [0] == 'JOIN':
                message = pickle.dumps([multicast_data.LEADER, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] Client {address} wants to join the Chat Room\n')

            if len(pickle.loads(data)[0]) == 0:
                multicast_data.SERVER_LIST.append(address[0]) if address[0] not in multicast_data.SERVER_LIST else multicast_data.SERVER_LIST
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_changed = True

            elif pickle.loads(data)[1] and multicast_data.LEADER != server_data.SERVER_IP or pickle.loads(data) [3]:
                multicast_data.SERVER_LIST = pickle.loads(data)[0]
                multicast_data.LEADER = pickle.loads(data)[1]
                multicast_data.CLIENT_LIST = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] All Data have been updated')
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_changed = True

        except KeyboardInterrupt:
            socket.close()
            print(f'[MULTICAST RECEIVER {server_data.SERVER_IP}] Closing UDP Socket')