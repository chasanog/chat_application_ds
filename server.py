import pickle
import socket
import sys

import multicast_data
import multicast_receiver
import multicast_sender
import ports
import server
import server_data
from time import sleep

from Bully import generate_node_id

import thread_helper

# Create a TCP socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# host_address = (server_data.SERVER_IP, ports.SERVER_PORT)


# Buffer size
buffer_size = 1024

# Message to be sent to client
message = 'Hi client! Nice to connect with you!'


def send_server_list():
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            if multicast_data.SERVER_LIST[i] != server_data.SERVER_IP:
                replica = multicast_data.SERVER_LIST[i]
                print(f'replica: {replica}')
                ip= replica

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)

                try:
                    sock.connect((ip, ports.SERVERLIST_UPDATE_PORT))

                    updated_list = pickle.dumps(multicast_data.SERVER_LIST)
                    sock.send(updated_list)
                    print(f'SENDING UPDATED LIST: {updated_list.decode()}')
                    try:
                        respone = sock.recv(1024).decode()
                        print(respone)
                    except socket.timeout:
                        print(f'no response from {ip}')
                except:
                    print(f'failed to send serverlist{ip}')
                finally:
                    sock.close()

def receive_server_list():
    server_address = ('', ports.SERVERLIST_UPDATE_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()

    while True:
        connection, leader_address = sock.accept()
        leader_list = pickle.loads(connection.recv(1024))

        new_list = []
        new_list = leader_list

        server_list_len = len(new_list)

        for i in range(server_list_len):
            replica = new_list[i]
            server_address = replica
            ip = server_address
            if ip == server_data.SERVER_IP:
                del new_list[i]
                new_list.append((leader_address[0]))
                multicast_data.SERVER_LIST = new_list
                print(f'NEW SERVER LIST {multicast_data.SERVER_LIST}')
                sleep(0.5)


def send_leader_data2():
    while True:
        if len(server_data.replica_data) == 0:
            print('no replica servers available')
        else:
            for i in range(len(server_data.replica_data)):
                replica = server_data.replica_data[i]
                ip, port = replica

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)

                try:
                    sock.connect((ip, port + 1))
                    serverList = pickle.dumps(multicast_data.SERVER_LIST)
                    sock.send(serverList)
                finally:
                    sock.close()


def send_leader_data():
    if multicast_data.LEADER == server_data.SERVER_IP:
        message = server_data.SERVER_IP

        for i in range(len(server_data.replica_data)):
            ip, port = server_data.replica_data[i]

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)

            try:
                sock.connect((ip, port + 1))
                sock.send(message.encode())
                print(f'Hey {ip} the Leader is: {multicast_data.LEADER}')
                try:
                    response = sock.recv(1024)
                    print(f'ack from {ip} is {response.decode()}')
                except socket.timeout:
                    pass
            finally:
                sock.close()


def receive_leader_message():
    server_address = ('', ports.SERVER_PORT_FOR_CLIENTS)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()

    while True:
        connection, server_address = sock.accept()
        leader_ip = connection.recv(1024).decode()
        for j in range(len(multicast_data.SERVER_LIST)):
            data = multicast_data.SERVER_LIST[j]
            ip, port = data
            if ip == leader_ip:
                multicast_data.LEADER = ip

        respones = 'ach msg Received new leader information'
        connection.send(respones.encode())
        """
        server_address = ('', replica[1])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(server_address)
        sock.listen()
        print('Listening now for leader messages')

        while True:
            connection, server_address = sock.accept()
            leader_ip = connection.recv(1024).decode()

            for j in range(len(multicast_data.SERVER_LIST)):
                data = multicast_data.SERVER_LIST[j]
                ip, port = data
                if ip == leader_ip:
                    multicast_data.LEADER = ip

            respones = 'ach msg Received new leader information'
            connection.send(respones.encode())
            
def get_new_connections(sock):
    while True:
        if multicast_data.LEADER == server_data.SERVER_IP:
            connection, server_address = sock.accept()
            
            if multicast_data.CLIENT_LIST:
              """

def bind_server_sock():
    try:
        # TCP Socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_address = (server_data.SERVER_IP, ports.SERVER_PORT_FOR_CLIENTS)
        print(f'Server started on IP {server_data.SERVER_IP} and PORT {ports.SERVER_PORT_FOR_CLIENTS}')

        server_socket.bind(host_address)
        server_socket.listen()
        print(f'Server is waiting for client connections...')
    except socket.error as err:
        print(f'Could not start Server. Error: {err}')
        sys.exit()

    # print(f'\n [SERVER INFO] Listening on IP {server_socket.getsockname()[0]} and PORT {ports.SERVER_PORT}')
    """
    while True:

        try:
            print('\nWaiting to receive message...\n')

            # Receive message from client
            client, address = server_socket.accept()
            data = client.recv(buffer_size)
            print("CLIENT ", client)
            print('Received message from client: ', address)
            print('Message: ', data.decode())

            if data:
                # Send message to client
                client.send(str.encode(message))
                print(f'Replied to client: ', message)
                break

        except Exception as err:
            print(err)
            break
    """

if __name__ == '__main__':

    """
    try:
        first_argv = sys.argv[1]
        if first_argv == 'leader' or 'Leader':
            print(f'New Leader is: {server_data.SERVER_IP}')
            isLeader=True
    except:
        pass

    thread_helper.newThread(bind_server_sock(), ())
    
    if isLeader == False:
    """

    multicastReceiver = multicast_sender.requestToMulticast()

    if not multicastReceiver:
        #multicast_data.SERVER_LIST.append(server_data.SERVER_IP)
        multicast_data.LEADER = server_data.SERVER_IP

    if multicast_data.LEADER != server_data.SERVER_IP:
        thread_helper.newThread(receive_server_list, ())

    thread_helper.newThread(multicast_receiver.start_receiver, ())
    thread_helper.newThread(bind_server_sock, ())

    while True:
        try:
            if multicast_data.LEADER and multicast_data.network_state:
                multicast_sender.requestToMulticast()
                multicast_data.network_state = False
                # thread_helper.newThread(send_leader_data, ())
                print('here')

            elif multicast_data.LEADER != server_data.SERVER_IP and multicast_data.network_state:
                multicast_data.network_state = False

                # server_list_update(server_data.replica_data)
                print('here 2')


        except KeyboardInterrupt:
            server_socket.close()
            print(f'\nClosing Server for IP {server_data.SERVER_IP} on PORT {ports.SERVER_PORT_FOR_CLIENTS}')
            break
