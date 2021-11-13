import socket
import server_data
import ports
import multicast_data

import pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, multicast_data.MULTICAST_TTL)


def requestToMulticast():
    sock.sendto(b"robot", (multicast_data.MCAST_GRP, multicast_data.MCAST_PORT))