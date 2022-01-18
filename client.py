import socket

# Create a UDP socket
import multicast_data
import multicast_sender
import ports
import server
import server_data
import os
import time
import pickle

import thread_helper

def receive_mesage():
    server_address = ('', ports.SERVER_CLIENT_MESSAGE_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()
    while True:
        connection, leader_address = sock.accept()
        message = pickle.loads(connection.recv(1024))
        print(message)

def check_leader_abailability():
    global client_socket

    while True:
        try:
            data = client_socket.recv(1024)
            print(data.decode('utf-8'))
            if not data:
                print("\nChat server currently not available."
                      "Please wait 5 seconds for reconnection with new server leader.")
                client_socket.close()
                time.sleep(5)

                # Start reconnecting to new server leader
                connect_to_server()
        except Exception as err:
            print(err)
            break

def disconnect_from_server():
    global client_socket

    message = 'disconnect'
    message = message.encode()
    client_socket.send(message)
    client_socket.close

def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check_server_exist = multicast_sender.requestToJoinChat()

    if check_server_exist:
        leader_address = (multicast_data.LEADER, ports.SERVER_PORT_FOR_CLIENTS)
        print(f'{leader_address}: Hi, welcome to the room let me connect you...')

        client_socket.connect(leader_address)
        client_socket.send('JOIN'.encode('utf-8'))
        print(f'You can start chatting now!')
        thread_helper.newThread(receive_mesage, ())
        thread_helper.newThread(check_leader_abailability, ())
        while True:
            message = input("")
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as err:
                print(err)
                break
    else:
        print('Did not work trying again if possible.')
        client_socket.close()

    connect_to_server()

if __name__ == '__main__':
    try:
        connect_to_server()
    except KeyboardInterrupt:
        print('\n You left the chat.')
        disconnect_from_server()

