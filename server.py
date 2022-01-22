import pickle
import socket
import sys

import heartbeat
import leader_election
import multicast_data
import multicast_receiver
import multicast_sender
import ports
import server_data
import logging
from time import sleep

import thread_helper

#logger configuration
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s')

# sends leader information over a TCP Socket
def send_leader():
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            replica = multicast_data.SERVER_LIST[i]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((replica, ports.LEADER_NOTIFICATION_PORT))
                leader_message = pickle.dumps(multicast_data.LEADER)
                sock.send(leader_message)
                logging.info(f'Leader {multicast_data.LEADER} is updating the leader parameter for {replica}')
                print(f'Updating Leader for {replica}')
            except:
                logging.critical(f'Failed to update leader address for {replica}')
                print(f'Failed to send Leader address to {replica}')
            finally:
                sock.close()

# listener to receiver Leader information for replica server
def receive_leader():
    server_address = ('', ports.LEADER_NOTIFICATION_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()

    while True:
        connection, leader_address = sock.accept()
        leader = pickle.loads(connection.recv(1024))
        
        multicast_data.LEADER = leader
        print(f'LEADER IS: {multicast_data.LEADER}')

# sends server List to replica servers over TCP
def send_server_list():
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            if multicast_data.SERVER_LIST[i] != server_data.SERVER_IP:
                replica = multicast_data.SERVER_LIST[i]
                ip = replica
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sleep(1)
                try:
                    sock.connect((ip, ports.SERVERLIST_UPDATE_PORT))

                    updated_list = pickle.dumps(multicast_data.SERVER_LIST)
                    sock.send(updated_list)
                    logging.info(f'Updating Server List for {ip}')
                    print(f'Updating Server List for {ip}')
                except:
                    logging.critical(f'failed to send serverlist {ip}')
                    print(f'failed to send serverlist {ip}')
                finally:
                    sock.close()

# listener to receive server list from leader over TCP
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
                update_server_list(multicast_data.SERVER_LIST)


# sends client messages to other clients over a TCP Socket
def send_new_client_message(ip, msg):
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.CLIENT_LIST) > 0:
        for i in range(len(multicast_data.CLIENT_LIST)):
            client = multicast_data.CLIENT_LIST[i]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            if ip != client:
                try:
                    sock.connect((client, ports.SERVER_CLIENT_MESSAGE_PORT))
                    if ip != client:
                        packed_msg = pickle.dumps(f'from {ip}: "{msg}"')
                        sock.send(packed_msg)
                        print(f'Sending Message for {client}')
                except Exception as err:
                    print(f'Failed to send Message to {client} with following error message: {err}')
                finally:
                    sock.close()

# used in a thread to unpack the client message and distribute with the send_new_client_message function to other clients
def new_client_message(client, address):
    while True:
        try:
            data = client.recv(1024)
            if data.decode('utf-8') != "":
                print(f'{server_data.SERVER_IP}: new Message from {address[0]}: {data.decode("utf-8")}')
                multicast_data.CLIENT_MESSAGES.append(f'{server_data.SERVER_IP}: new Message from {address[0]}: {data.decode("utf-8")}')
                send_new_client_message(address[0], data.decode('utf-8'))
                #print(f'CLIENT LIST {multicast_data.CLIENT_LIST}')
        except Exception as err:
            print(err)
            break

# main function which starts the server on TCP Socket
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

        while True:
            try:
                client, address = server_socket.accept()
                client_data = client.recv(1024)

                if client_data:
                    print(f'{server_data.SERVER_IP}: Client {address[0]} is now connected')
                    thread_helper.newThread(new_client_message, (client, address))
            except Exception as err:
                print(err)
                break
    except socket.error as err:
        print(f'Could not start Server. Error: {err}')
        sys.exit()

# this function will be executed depending on Heartbeat activity and updates server list accordingly
def update_server_list(new_list):
    if len(multicast_data.SERVER_LIST) == 0:
        server_data.HEARTBEAT_RUNNING = False
        server_data.HEARTBEAT_COUNT = 0

        if multicast_data.LEADER != server_data.SERVER_IP:
            multicast_data.LEADER = server_data.SERVER_IP
            print(f'My server list is empty, the new leader is me {server_data.SERVER_IP}')

    elif len(multicast_data.SERVER_LIST) > 0:
        if server_data.HEARTBEAT_COUNT == 0:
            server_data.HEARTBEAT_COUNT += 1
            sleep(1)
            print(f'NEW LIST {list(set(new_list))}')
            multicast_data.SERVER_LIST = list(set(new_list))

            print(f'Heartbeat starting for the first time with the server list containing: {multicast_data.SERVER_LIST}')
            server_data.HEARTBEAT_RUNNING = True
            thread_helper.newThread(heartbeat.start_heartbeat, ())

        else:
            multicast_data.SERVER_LIST = list(set(new_list))
            server_data.isReplicaUpdated = True

# sends client list to other server over TCP
def send_client_list():
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            if multicast_data.SERVER_LIST[i] != server_data.SERVER_IP:
                ip = multicast_data.SERVER_LIST[i]
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    sock.connect((ip, ports.CLIENT_LIST_UPDATE_PORT))

                    updated_list = pickle.dumps(multicast_data.CLIENT_LIST)
                    sock.send(updated_list)
                    logging.info(f'Updating Client List for {ip}')
                    print(f'Updating Client List for {ip}')
                except:
                    logging.critical(f'failed to send Client List to {ip}')
                    print(f'failed to send Client list to {ip}')
                finally:
                    sock.close()

# listener for replica server to receive the client list
def receive_client_list():
    server_address = ('', ports.CLIENT_LIST_UPDATE_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()

    while True:
        connection, leader_address = sock.accept()
        leader_list = pickle.loads(connection.recv(1024))

        new_list = []
        new_list = leader_list

        multicast_data.CLIENT_LIST = new_list
        print(f'NEW CLIENT LIST {multicast_data.CLIENT_LIST}')


if __name__ == '__main__':
    multicastReceiver = multicast_sender.requestToMulticast()

    # checking if multicast receiver is available
    if not multicastReceiver:
        multicast_data.LEADER = server_data.SERVER_IP
        server_data.LEADER_CRASH = False
        server_data.LEADER_AVAILABLE = True

    thread_helper.newThread(multicast_receiver.start_receiver, ())
    thread_helper.newThread(bind_server_sock, ())

    thread_helper.newThread(receive_server_list, ())
    thread_helper.newThread(receive_leader, ())
    thread_helper.newThread(heartbeat.listen_heartbeat, ())
    thread_helper.newThread(leader_election.listenforNewLeaderMessage, ())
    thread_helper.newThread(leader_election.receive_election_message, ())
    thread_helper.newThread(receive_client_list, ())

    while True:
        try:
            if multicast_data.LEADER and multicast_data.network_state:
                multicast_sender.requestToMulticast()
                multicast_data.network_state = False

            elif multicast_data.LEADER != server_data.SERVER_IP and multicast_data.network_state:
                multicast_data.network_state = False

        except KeyboardInterrupt:
            print(f'\nClosing Server for IP {server_data.SERVER_IP} on PORT {ports.SERVER_PORT_FOR_CLIENTS}')
            break
