import socket

# Create a UDP socket
import multicast_data
import multicast_sender
import ports
import server
import server_data
import os
import pickle

import thread_helper

def receive_mesage():
    server_address = ('', ports.SERVER_TO_CLIENT_MESSAGE_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()
    while True:
        try:
            client, address = sock.accept()
            message = pickle.loads(client.recv(1024))
            if message:
                print(f'{address[0]}: New Message {message}')
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
        while True:
            message = input("")
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as err:
                print(err)
                break
    else:
        print('Did not work please try again later.')
        client_socket.close()

if __name__ == '__main__':
    try:
        connect_to_server()

    except KeyboardInterrupt:
        print('\n You left the chat.')
        disconnect_from_server()

