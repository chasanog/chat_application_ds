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

neighbour = ''
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

# Publish new leader ip address
def sendnewLeaderMessage():
    if multicast_data.LEADER == server_data.SERVER_IP:
        # New Leader IP
        #multicast_data.LEADER = get_neighbour(form_ring(multicast_data.SERVER_LIST), multicast_data.LEADER)
        msg = server_data.SERVER_IP

        for x in range(len(multicast_data.SERVER_LIST)):
            ip = multicast_data.SERVER_LIST[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
            s.settimeout(2)  # set timeout for every socket to 1 seconds
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

        print(f'Received newLeaderMessage. New leader is: {newleader_ip} {server_data.LEADER_AVAILABLE}')
        print('Received newLeaderMessage: new leader is:', newleader_ip)
        multicast_data.LEADER = newleader_ip

def start_leader_election(server_list, ip):
    current_participants = []
    current_participants.append(ip)

    for i in range(len(server_list)):
        server_address = server_list[i]
        current_participants.append(server_address)

    if len(server_list) == 1:
        global neighbour
        neighbour = server_list[0]
        print(f'There is only one neighbour: {neighbour}')
        send_election_message(ip)
    else:
        ring = form_ring(current_participants)
        neighbour = get_neighbour(ring, ip, 'right')
        print(f'Ring of Hosts: {ring} My IP: {ip}, My neighbour: {neighbour}')
        send_election_message(ip)


def send_election_message(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)

    try:
        sock.connect((neighbour, ports.SERVER_ELECTION_PORT))
    except:
        print('Connecting to neighbour was not possible')

    try:
        sleep(1)
        print(f'Sending election message to {neighbour}: "{msg}"')
        sock.send(msg.encode())
    except:
        print('Message could not be delivered')
    finally:
        sock.close()

    pass

def receive_election_message():
    server_address = ('', ports.SERVER_ELECTION_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen()
    while True:
        conn, address = sock.accept()
        response = conn.recv(1024)
        response = response.decode()
        sleep(2)
        print(f'Received {response} from leader election')

        if response == server_data.SERVER_IP:
            print('Received my IP so I am the new Leader')
            multicast_data.LEADER = server_data.SERVER_IP
            sendnewLeaderMessage()
        elif response > server_data.SERVER_IP:
            print(f'{response} is higher than {server_data.SERVER_IP}. Giving higher IP to neighbour')
            send_election_message(response)
        else:
            print(f'Received IP is not higher than mine.')

