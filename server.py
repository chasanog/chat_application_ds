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

def send_leader():
    #sender_template(multicast_data.LEADER, server_data.SERVER_IP, multicast_data.SERVER_LIST, ports.LEADER_NOTIFICATION_PORT, "leader")
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            replica = multicast_data.SERVER_LIST[i]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((replica, ports.LEADER_NOTIFICATION_PORT))
                leader_message = pickle.dumps(multicast_data.LEADER)
                sock.send(leader_message)
                print(f'Updating Leader for {replica}')
            except:
                print(f'Failed to send Leader address to {replica}')
            finally:
                sock.close()

"""
def sender_template(leader, server_ip, server_list, port, msg):
    if leader == server_ip and len(server_list) > 0:
        for i in range(len(server_list)):
            if server_list[i] != server_ip:
                replica = server_list[i]
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    sock.client((replica, port))
                    message = pickle.dumps(leader)
                    sock.send(message)
                    print(f'Updating Leader for {msg}')
                    
                    try:
                        response = sock.recv(1024).decode()
                        print(response)
                    except socket.timeout:
                        print(f'no respones to {msg} update from {replica}')
                   
                except:
                    print(f'Failed to send {msg} to {replica}')
                finally:
                    sock.close()

"""
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

def send_server_list():
    #sender_template(multicast_data.LEADER, server_data.SERVER_IP, multicast_data.SERVER_LIST, ports.SERVERLIST_UPDATE_PORT)
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.SERVER_LIST) > 0:
        for i in range(len(multicast_data.SERVER_LIST)):
            if multicast_data.SERVER_LIST[i] != server_data.SERVER_IP:
                replica = multicast_data.SERVER_LIST[i]
                ip = replica
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)

                try:
                    sock.connect((ip, ports.SERVERLIST_UPDATE_PORT))

                    updated_list = pickle.dumps(multicast_data.SERVER_LIST)
                    sock.send(updated_list)
                    print(f'Updating Server List for {ip}')
                    """
                    try:
                        response = sock.recv(1024).decode()
                        print(response)
                    except socket.timeout:
                        print(f'no response to server list update from {ip}')
                    """
                except:
                    print(f'failed to send serverlist {ip}')
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






            """
def get_new_connections(sock):
    while True:
        if multicast_data.LEADER == server_data.SERVER_IP:
            connection, server_address = sock.accept()
            
            if multicast_data.CLIENT_LIST:
              """

def receive_new_message():
    server_address = ('', ports.SERVER_CLIENT_MESSAGE_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()
    while True:
        connection, leader_address = sock.accept()
        message = pickle.loads(connection.recv(1024))
        print(message.decode('uft-8'))


def send_new_client_message(ip, msg):
    if multicast_data.LEADER == server_data.SERVER_IP and len(multicast_data.CLIENT_LIST) > 0:
        for i in range(len(multicast_data.CLIENT_LIST)):
            client = multicast_data.CLIENT_LIST[i]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((client, ports.SERVER_TO_CLIENT_MESSAGE_PORT))
                if ip != client:
                    packed_msg = pickle.dumps(f'from {ip}: "{msg}"')
                    sock.send(packed_msg)
                    print(f'Sending Message for {client}')
            except:
                print(f'Failed to send Message to {client}')
            finally:
                sock.close()

def new_client_message(client, address):
    while True:
        try:
            data = client.recv(1024)
            if data.decode('utf-8') != "":
                print(f'{server_data.SERVER_IP}: new Message from {address[0]}: {data.decode("utf-8")}')
                send_new_client_message(address[0], data.decode('utf-8'))
                print(f'CLIENT LIST {multicast_data.CLIENT_LIST}')
        except Exception as err:
            print(err)
            break

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
        thread_helper.newThread(receive_leader, ())

    thread_helper.newThread(multicast_receiver.start_receiver, ())
    thread_helper.newThread(bind_server_sock, ())

    while True:
        try:
            if multicast_data.LEADER and multicast_data.network_state:
                multicast_sender.requestToMulticast()
                multicast_data.network_state = False

            elif multicast_data.LEADER != server_data.SERVER_IP and multicast_data.network_state:
                multicast_data.network_state = False

        except KeyboardInterrupt:
            #socket.close()
            print(f'\nClosing Server for IP {server_data.SERVER_IP} on PORT {ports.SERVER_PORT_FOR_CLIENTS}')
            break
