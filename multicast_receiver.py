import pickle
import socket
import struct

import multicast_data
import server
import server_data

multicastIP = multicast_data.MCAST_GRP
serverAddress = ('', multicast_data.MCAST_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def pickle_load_reader(data, pos):
    return pickle.loads(data)[pos]

def start_receiver():
    sock.bind(serverAddress)

    #WTH
    group = socket.inet_aton(multicastIP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n{server_data.SERVER_IP}: Started UDP Socket to listen on Port {multicast_data.MCAST_PORT}')

    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f'{server_data.SERVER_IP}: Received data from {address} \n')

            if multicast_data.LEADER == server_data.SERVER_IP and pickle.loads(data) [0] == 'JOIN':
                message = pickle.dumps([multicast_data.LEADER, ''])
                sock.sendto(message, address)
                print(f'{server_data.SERVER_IP}: "{address}" wants to join the Chat Room\n')

            if len(pickle_load_reader(data, 0)) == 0:
                multicast_data.SERVER_LIST.append((address[0], False)) if address[0] not in multicast_data.SERVER_LIST else multicast_data.SERVER_LIST
                print(f'{server_data.SERVER_IP}: replica server joined {address}')
                server.update_server_list(multicast_data.SERVER_LIST)
                server.send_updated_server_list()
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_state = True

            elif pickle_load_reader(data, 1) and multicast_data.LEADER != server_data.SERVER_IP or pickle_load_reader(data, 3):
                multicast_data.SERVER_LIST = pickle_load_reader(data, 0)
                multicast_data.LEADER = pickle_load_reader(data, 1)
                multicast_data.CLIENT_LIST = pickle_load_reader(data, 4)
                print(f'{server_data.SERVER_IP}: Data has been updated')
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_state = True

        except KeyboardInterrupt:
            socket.close()
            print(f'{server_data.SERVER_IP}: Closing Socket')