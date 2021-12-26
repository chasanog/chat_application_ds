import pickle
import socket
import sys

import multicast_data
import multicast_receiver
import multicast_sender
import ports
import server
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

isLeader = False

def update_server_list(serverList):
    #TODO Heartbeat
    if server.isLeader == False:
        server.isLeader = True
        print(f'Server list is empty. New Leader is {server_data.SERVER_IP}')

    #elif len(serverList) > 0:
        #TODO Heartbeat

    else:
        serverList = serverList
        print(f'New Server list is: {serverList}')

def send_updated_server_list():
    if isLeader == True:
        for i in range(len(multicast_data.SERVER_LIST)):
            serverAddress, leader = multicast_data.SERVER_LIST[i]

            #TODO
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)

            try:
                newServerList = pickle.dumps(multicast_data.SERVER_LIST)
                sock.send(newServerList)
            except:
                print(f'Server {serverAddress} not reachable. Server List could not be updated')
            finally:
                sock.close()
    else:
        print(f'Server List is empty. Doing nothing.')


def bind_server_sock():
    try:
        #TCP Socket
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
        multicast_data.SERVER_LIST.append(server_data.SERVER_IP)
        multicast_data.LEADER = server_data.SERVER_IP
        isLeader = True

    thread_helper.newThread(multicast_receiver.start_receiver, ())
    thread_helper.newThread(bind_server_sock, ())


    while True:
        try:
            if isLeader and multicast_data.network_state:
                multicast_sender.requestToMulticast()
                multicast_data.network_state = False

            elif isLeader == False and multicast_data.network_state:
                multicast_data.network_state = False


        except KeyboardInterrupt:
            server_socket.close()
            print(f'\nClosing Server for IP {server_data.SERVER_IP} on PORT {ports.SERVER_PORT}')
            break
