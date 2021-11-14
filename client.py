import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server application IP address and port
server_address = '127.0.0.1'
server_port = 10001

# Buffer size
buffer_size = 1024

# Message sent to server
message = 'Hi server!'
address_toConnect = (server_address, server_port)
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

    #Dies ist die Branch Version
