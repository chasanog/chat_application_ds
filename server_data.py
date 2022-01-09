import socket

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_SOCKET.connect(("8.8.8.8", 80))
SERVER_IP = SERVER_SOCKET.getsockname()[0]

LEADER_CRASH = False
LEADER_AVAILABLE = False

HEARTBEAT_RUNNING = False
HEARTBEAT_COUNT = 0

isReplicaUpdated = False
replica_data = []