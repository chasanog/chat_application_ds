import socket

import multicast_sender
import ports
import server_data

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (server_data.SERVER_IP, ports.SERVER)

# Server application IP address and port
server_address = '127.0.0.1'
server_port = 10001

# Buffer size
buffer_size = 1024

# Message to be sent to client
message = 'Hi client! Nice to connect with you!'

# Bind socket to port
server_socket.bind((server_address, server_port))
server_socket.listen()
print('Server up and running at {}:{}'.format(server_address, server_port))

while True:
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


if __name__ == '__main__':
    multicastReceiver = multicast_sender.requestToMulticast()
