import pickle
import socket
import struct

import multicast_data
import server
import server_data
import thread_helper

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
            if address[0] != server_data.SERVER_IP:
                print(f'{server_data.SERVER_IP}: Received data from {address} \n')
            if multicast_data.LEADER == server_data.SERVER_IP and pickle.loads(data)[0] == 'JOIN':
                multicast_data.CLIENT_LIST.append(address[0]) if address[
                                                                     0] not in multicast_data.CLIENT_LIST else multicast_data.CLIENT_LIST
                message = pickle.dumps([multicast_data.LEADER, ''])
                sock.sendto(message, address)
                server.send_client_list()
                print(f'{server_data.SERVER_IP}: "{address}" wants to join the Chat Room\n')

            if len(pickle_load_reader(data, 0)) == 0:
                multicast_data.SERVER_LIST.append(address[0]) if address[0] not in multicast_data.SERVER_LIST else multicast_data.SERVER_LIST
                print(f'{server_data.SERVER_IP}: replica server joined {address}')
                server_data.replica_data.append(address)
                server.update_server_list(multicast_data.SERVER_LIST)
                server.send_server_list()
                server.send_leader()
                print(server_data.replica_data)
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_state = True
            elif pickle.loads(data)[0] != 'JOIN' and multicast_data.LEADER != server_data.SERVER_IP:
                sock.sendto('ack'.encode('utf-8'), address)
                multicast_data.network_changed = True

        except KeyboardInterrupt:
            socket.close()
            print(f'{server_data.SERVER_IP}: Closing Socket')


