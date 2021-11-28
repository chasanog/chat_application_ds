import socket

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.connect(("8.8.8.8", 80))
SERVER_IP = SERVER_SOCKET.getsockname()[0]
server_port = 10001

# Buffer size
buffer_size = 1024

message = 'Hi client! Nice to connect with you!'

# Bind socket to port
server_socket.bind((SERVER_IP, server_port))
print('Server up and running at {}:{}'.format(SERVER_IP, server_port))

while True:
    print('\nWaiting to receive message...\n')

    data, address = server_socket.recvfrom(buffer_size)
    print('Received message from client: ', address)
    print('Message: ', data.decode())

    if data:
        server_socket.sendto(str.encode(message), address)
        print('Replied to client: ', message)