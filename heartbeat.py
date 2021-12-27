"""
Date:   25.12.2021
Group:  10

"""


import socket
import sys
import time

import ports
from server import *

# used from Server

def start_heartbeat():
    msg = ("Heartbeat")
    for x in range(len(multicast_data.SERVER_LIST)):
        ip = multicast_data.SERVER_LIST[x]
        # Create TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Timeout socket 2s
        s.settimeout(2)

        try:
            # Connect each socket to ip and heartbeat Port
            s.connect((ip, ports.HEARTBEAT_PORT))
            s.send(msg.encode())
            print("Sending Heartbeat: Heartbeat msg sent to: {},{} ".format(ip, ports.HEARTBEAT_PORT))

            try:
                response = s.recv(1024)
                print("Sending Heartbeat: Received Heartbeat response: {}".format(response.decode()))

            except socket.timeout:
                print('Sending Heartbeat: No response to heartbeat from: {} '.format(ip))
                # if no response is received remove server from list

        except:
            print("Sending Heartbeat: Server not online can't connect to: {},{} ".format(ip, ports.HEARTBEAT_PORT))
            # Position of failed server in the server list
            failed_server = x
            # Crashed server is the leader
            if multicast_data.LEADER == server_data.SERVER_IP:
                print('Leader crash detected')
                # Remove crashed leader from serverlist
                multicast_data.SERVER_LIST.pop(failed_server)

            else:
                # Remove crashed server from serverlist
                multicast_data.SERVER_LIST.pop(failed_server)

        finally:
            s.close()



def listenHeartbeat():

    server_address = ('', ports.HEARTBEAT_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_address)
    s.listen()
    print('Listening to Heartbeat on Port: {} '.format(ports.HEARTBEAT_PORT))
    while True:
        connection, server_address = s.accept()  # Wait for a connection
        heartbeat_msg = connection.recv(1024)
        heartbeat_msg = heartbeat_msg.decode()
        print('Listening Heartbeat: received Heartbeat from: {} '.format(server_address))
        if heartbeat_msg:
            print('Listening Heartbeat: sending Heartbeat back to: {} '.format(server_address))
            connection.sendall(heartbeat_msg.encode())
