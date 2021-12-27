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

import server_data
from server import *


def sendnewLeaderMessage(self):
    if server_data.LEADER_AVAILABLE == True:
        msg = server_data.SERVER_IP  # IP of new leader

        for x in range(len(self.serverlist)):
            connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
            server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
            ip, port = server_adress  # split up server_adress into ip adress and port

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
            s.settimeout(1)  # set timeout for every socket to 1 seconds
            try:
                s.connect((ip, SERVER_NEW_LEADER_MESSAGE_PORT))  # Connect to every servers socke to inform about new leader
                s.send(message.encode())
                logging.info("Sent newLeaderMessage to: {},{} ".format(ip, SERVER_NEW_LEADER_MESSAGE_PORT))
                print('Sending newLeaderMessage to ', ip)
                try:
                    response = s.recv(1024)
                    logging.info("Received ack from sent newLeaderMessage from: {}".format(ip, response.decode()))
                except socket.timeout:
                    pass
            finally:
                s.close()  # Close socket


def listenforNewLeaderMessage(self):
    server_address = ('', SERVER_NEW_LEADER_MESSAGE_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    sock.bind(server_address)  # Bind to the server address
    sock.listen()
    logging.info('Listening to NewLeaderMessage on Port: {} '.format(SERVER_NEW_LEADER_MESSAGE_PORT))
    while True:
        connection, server_address = sock.accept()  # Wait for a connection
        newleader_ip = connection.recv(1024)
        newleader_ip = newleader_ip.decode()

        for i in range(len(self.serverlist)):  # search for the leader IP in the serverlist
            connection_and_leader = self.serverlist[
                i]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
            server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
            ip, port = server_adress  # split up server_adress into ip adress and port
            if ip == newleader_ip:  # When ip in list matches the leader ip change the isLeader value to True
                self.serverlist[
                    i] = server_adress, True  # Overwrite old value with new value. Same adress but True for new leader

        response = 'ack msg.Received new leader information'  # send back ack msg
        connection.send(response.encode())

        logging.info('Received newLeaderMessage. New leader is:'.format(newleader_ip, isLeader))
        print('Received newLeaderMessage: new leader is:', newleader_ip)
        print('Updated my serverlist: ', self.serverlist)


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


def listenforNewLeaderOrderlistRequest(self):
    server_address = ('', SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    sock.bind(server_address)  # Bind to the server address
    sock.listen()
    logging.info(
        'Waiting for new Leader to request Orderlist on Port: {} '.format(SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT))
    while True:
        connection, server_address = sock.accept()  # Wait for a connection
        leader_ordernumber = connection.recv(1024)
        leader_ordernumber = pickle.loads(leader_ordernumber)
        print('Received ordernumber from leader:', leader_ordernumber)

        if self.ordernumber == leader_ordernumber or self.ordernumber < leader_ordernumber:
            print('Ordernumber identical with leader server')
            response = 'no'  # there are no updates
            connection.send(response.encode())
        else:
            print('My ordernumer is higher than leader order number. Sending order updates')
            message = pickle.dumps(self.orderlist)
            connection.send(message)


def getLatestOrderlistfromServer(self):
    for x in range(len(self.serverlist)):
        connection_and_leader = self.serverlist[
            x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
        server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
        ip, port = server_adress  # split up server_adress into ip adress and port

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
        s.settimeout(2)  # set timeout for every socket to 1 seconds

        try:
            s.connect((ip, SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT))  # Connect to each member server
            ordernumber = pickle.dumps(self.ordernumber)
            s.send(ordernumber)  # send ordernumber and wait for the response

            response = s.recv(1024)
            try:
                response = pickle.loads(response)
            except:
                response = response.decode()

            if response == 'no':
                logging.info('New Leader: Orderlist of leader server and server {} is identical '.format(
                    ip))  # Do nothing continue with for loop and ask next member server
                print('New Leader: Orderlist of leader server and server', ip, ' is identical')
            else:
                self.orderlist = response
                self.ordernumber = len(self.orderlist)
                print('Restored latest list form server', ip)
                print('Current orderlist:', self.orderlist, 'Current ordernumber:', self.ordernumber)

        except:
            print('Could not connect or send msg to:', ip, ',', SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT)
        finally:
            s.close()


def getLatestOrderlistfromClient(self):
    for x in range(len(self.clientlist)):
        client_ip, client_port = self.clientlist[x]
        client_order_request_port = client_port + 200  # this is the port where every client is listening for requests for missed orders

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
        s.settimeout(2)  # set timeout for every socket to 1 seconds

        leader_ordernumber_msg = pickle.dumps(self.ordernumber)

        try:
            s.connect(
                (client_ip, client_order_request_port))  # Connect to every servers socke to inform about new leader
            s.send(leader_ordernumber_msg)

            response = s.recv(1024)
            try:  # if the client has no higher orderid response will be 'no' which is string
                response = response.decode()
                print('Client', self.clientlist[x], 'has no missed orders')
            except:  # if response can not be decoded it means it's no string. It will be list of missed orders
                missed_order_list = []
                missed_order_list = pickle.loads(response)

                for i in range(len(missed_order_list)):
                    self.orderlist.append(missed_order_list[i])
                    self.ordernumber += 1

                print('Client', self.clientlist[x], 'has sent', len(missed_order_list), 'missed orders')
                self.orderlist.sort(key=lambda x: x[0])  # after adding missed orders. Sort orderlist


        except:
            pass  # if connection cant be establish client is offline
    print('Latest orderlist:', self.orderlist)
