"""
Date:       25.12.2021  
Group:      10

ring-algorithm - Server leader election
"""
# import Modules
import os
import struct
import sys
import threading
import socket
import pickle #is needed so send objects (tuple,list) through tcp
import logging

import multicast_data
import ports
import server_data
from server import *


# Sorted Ip
def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    print(sorted_binary_ring)
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    print(sorted_ip_ring)
    return sorted_ip_ring

# get neighbour of IP
def get_neighbour(ring, current_node_ip, direction='left'):
    current_node_index = ring.index(current_node_ip) if current_node_ip in ring else -1
    if current_node_index != -1:
        if direction == 'left':
            if current_node_index + 1 == len(ring):
                return ring[0]
            else:
                return ring[current_node_index + 1]
        else:
            if current_node_index == 0:
                return ring[len(ring) - 1]
            else:
                return ring[current_node_index - 1]
    else:
        return None

# Publish new leader ip
def sendnewLeaderMessage():
    if server_data.LEADER_AVAILABLE == False:
        # New Leader IP
        multicast_data.LEADER = get_neighbour(form_ring(multicast_data.SERVER_LIST), multicast_data.LEADER)
        msg = multicast_data.LEADER

        for x in range(len(multicast_data.SERVER_LIST)):
            ip = multicast_data.SERVER_LIST[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
            s.settimeout(1)  # set timeout for every socket to 1 seconds
            try:
                s.connect((ip, ports.NEW_LEADER_PORT))  # Connect to every servers socke to inform about new leader
                s.send(msg.encode())
                print("Sent newLeaderMessage to: {},{} ".format(ip, ports.NEW_LEADER_PORT))
                print('Sending newLeaderMessage to ', ip)
                try:
                    response = s.recv(1024)
                    print("Received ack from sent newLeaderMessage from: {}".format(ip, response.decode()))
                except socket.timeout:
                    pass
            finally:
                s.close()  # Close socket


def listenforNewLeaderMessage():
    server_address = ('', ports.NEW_LEADER_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    s.bind(server_address)  # Bind to the server address
    s.listen()
    print('Listening to NewLeaderMessage on Port: {} '.format(ports.NEW_LEADER_PORT))
    while True:
        connection, server_address = s.accept()  # Wait for a connection
        newleader_ip = connection.recv(1024)
        newleader_ip = newleader_ip.decode()

        for i in range(len(multicast_data.SERVER_LIST)):  # search for the leader IP in the serverlist
            ip = multicast_data.SERVER_LIST[i]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port

        response = 'ack msg.Received new leader information'  # send back ack msg
        connection.send(response.encode())

        print('Received newLeaderMessage. New leader is:'.format(newleader_ip, server_data.LEADER_AVAILABLE))
        print('Received newLeaderMessage: new leader is:', newleader_ip)
"""
def listenforElectionMessage(self):
    server_address = ('', SERVER_LEADER_ELECTION_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    sock.bind(server_address)  # Bind to the server address
    sock.listen()
    logging.info('Listening for LCR Election messages on Port: {} '.format(SERVER_LEADER_ELECTION_PORT))
    while True:
        connection, server_address = sock.accept()  # Wait for a connection
        received_ip = connection.recv(1024)
        received_ip = received_ip.decode()  # Otherwise it is a IP and election is still running
        sleep(2)
        logging.info('Listening LCR Election messages: received election message: {} from {} '.format(received_ip,
                                                                                                      server_address))

        if socket.inet_aton(received_ip) == socket.inet_aton(host_ip_address):  # If I received my IP. I am the leader
            print("Leader Election: I'm the new leader")
            self.isLeader = True
            self.sendnewLeaderMessage()  # Inform other servers about the new leader

            print('Checking for orderlist updates on member servers')

            self.getLatestOrderlistfromServer()

            if len(self.clientlist) > 0:
                print('Checking for orderlist updates on clients')
                self.getLatestOrderlistfromClient()

            if self.ordernumber > 0:
                print('Restarting orderlist update thread')
                thread = threading.Thread(target=self.sendOrderlistUpdate)
                thread.start()

        elif socket.inet_aton(received_ip) > socket.inet_aton(
                host_ip_address):  # e.g 192.168.0.67 > 192.168.0.55, if received IP is higher pass on to neighbor
            print('Received IP(', received_ip, ') is higher than own(', host_ip_address,
                  '). Passing higher IP to neighbour')
            sendElectionmessage(received_ip)
        else:
            print('Received IP(', received_ip, ') is lower than own(', host_ip_address, ') Not passing to my neighbour')
"""
