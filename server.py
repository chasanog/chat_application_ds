import socket

import multicast_data
import multicast_receiver
import multicast_sender
import ports
import server_data

from Bully import generate_node_id

import thread_helper


# Create a TCP socket
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#host_address = (server_data.SERVER_IP, ports.SERVER_PORT)


# Buffer size
buffer_size = 1024

# Message to be sent to client
message = 'Hi client! Nice to connect with you!'

# Bind socket to port
#server_socket.bind(host_address)
#server_socket.listen()
#print('Server up and running at {}:{}'.format(server_data.SERVER_IP, ports.SERVER_PORT))

def bind_server_sock():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_address = (server_data.SERVER_IP, ports.SERVER_PORT)
        print(f'Server started on IP {server_data.SERVER_IP} and PORT {ports.SERVER_PORT}')

        server_socket.bind(host_address)
        server_socket.listen()
        print(f'Server is waiting for client connections...')
    except socket.error as err:
        print(f'Could not start Server. Error: {err}')

    #print(f'\n [SERVER INFO] Listening on IP {server_socket.getsockname()[0]} and PORT {ports.SERVER_PORT}')

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





if __name__ == '__main__':
    multicastReceiver = multicast_sender.requestToMulticast()

    if not multicastReceiver:
        multicast_data.SERVER_LIST.append(server_data.SERVER_IP)
        multicast_data.LEADER = server_data.SERVER_IP
    thread_helper.newThread(multicast_receiver.start_receiver(), ())
    thread_helper.newThread(bind_server_sock(), ())


    while True:
        try:
            if multicast_data.LEADER == server_data.SERVER_IP and multicast_data.network_state_changed:
                multicast_sender.requestToMulticast()
                multicast_data.network_state_changed = False

            elif multicast_data.LEADER != server_data.SERVER_IP and multicast_data.network_state_changed:
                multicast_data.network_state_changed = False


        except KeyboardInterrupt:
            server_socket.close()
            print(f'\nClosing Server for IP {server_data.SERVER_IP} on PORT {ports.SERVER_PORT}')
            break
