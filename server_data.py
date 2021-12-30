import socket

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.connect(("8.8.8.8", 80))
SERVER_IP = SERVER_SOCKET.getsockname()[0]

LEADER_CRASH = False
LEADER_AVAILABLE = True

replica_data = []