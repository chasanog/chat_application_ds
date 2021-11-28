import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.connect(("8.8.8.8", 80))
SERVER_IP = SERVER_SOCKET.getsockname()[0]

# Buffer size
buffer_size = 1024

# Message sent to server
message = 'Hi server!'
address_toConnect = (SERVER_IP, 10001)
client_socket.connect(address_toConnect)

try:
    # Send data to server
    client_socket.send(message.encode())
    print('Sent to server: ', message)

    # Receive response from server
    print('Waiting for response...')
    #server_data, server = client_socket.accept()
    data = client_socket.recv(buffer_size)
    print('Received message from server: ', data.decode())

finally:
    client_socket.close()
    print('Socket closed')
