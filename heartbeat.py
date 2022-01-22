"""
Date:   25.12.2021
Group:  10

"""
import socket
import server
import server_data
import time
import multicast_data
import ports
import logging
import thread_helper
import leader_election

# used to start heartbeat from server


def start_heartbeat():
    failed_server = -1
    msg = ("Heartbeat")
    while server_data.HEARTBEAT_RUNNING:
        time.sleep(3)  # failure detection every 3 seconds
        multicast_data.SERVER_LIST = list(set(multicast_data.SERVER_LIST))
        for x in range(len(multicast_data.SERVER_LIST)):
            time.sleep(1)
            if x > len(multicast_data.SERVER_LIST):
                server.update_server_list(multicast_data.SERVER_LIST)
                server.send_server_list()
                break
            if server_data.isReplicaUpdated == True:
                server_data.HEARTBEAT_RUNNING = False
                break
            time.sleep(1)
            print(multicast_data.SERVER_LIST)
            try:
                ip = multicast_data.SERVER_LIST[x]
            except IndexError:
                multicast_data.SERVER_LIST = list(set(multicast_data.SERVER_LIST))
                server.send_server_list()
                break

            # Create TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Timeout socket 2s
            s.settimeout(2)
            try:
                # Connect each socket to ip and heartbeat Port
                s.connect((ip, ports.HEARTBEAT_PORT))
                s.send(msg.encode())
                logging.info(f'Sending Heartbeat: Heartbeat msg sent to: {ip},{ports.HEARTBEAT_PORT}')
                #print(f'Sending Heartbeat: Heartbeat msg sent to: {ip},{ports.HEARTBEAT_PORT}')

                try:
                    response = s.recv(1024)
                    logging.info(f'Sending Heartbeat: Received Heartbeat response: {response.decode()}')
                    #print(f'Sending Heartbeat: Received Heartbeat response: {response.decode()}')

                except socket.timeout:
                    logging.warning(f'Sending Heartbeat: No response to heartbeat from: {ip}')
                    #print(f'Sending Heartbeat: No response to heartbeat from: {ip}')

            except:
                logging.warning(f'Sending Heartbeat: Server not online can not connect to: {ip},{ports.HEARTBEAT_PORT}')
                #print(f'Sending Heartbeat: Server not online can not connect to: {ip},{ports.HEARTBEAT_PORT}')
                # Position of failed server in the server list
                failed_server = x
                # Crashed server is the leader
                if multicast_data.LEADER == ip:
                    logging.info('Leader crash detected')
                    print('Leader crash detected')
                    # Remove crashed leader from serverlist
                    server_data.LEADER_CRASH = True
                    server_data.LEADER_AVAILABLE = False
                    logging.info(f'Removed crashed leader server {ip} from serverlist')
                    print(f'Removed crashed leader server {ip} from serverlist')
                else:
                    # Remove crashed server from serverlist
                    logging.info(f'Removed crashed server {ip} from serverlist')
                    print('Removed crashed server', ip, 'from serverlist')
                del multicast_data.SERVER_LIST[failed_server]
            finally:
                s.close()
        if failed_server >= 0:
            new_server_list = multicast_data.SERVER_LIST
            if server_data.LEADER_CRASH:
                logging.info(f'Leader Server {ip} crashed and removed from the Server list')
                print(f'Leader Server {ip} crashed and removed from the Server list')
            else:
                logging.info(f'Removed crashed server: {ip}')
                print(f'Removed crashed server: {ip}')
            server.update_server_list(new_server_list)
            server_data.HEARTBEAT_RUNNING = False
            break

        if server_data.HEARTBEAT_RUNNING == False:
            print('Heartbeat stopped')
            break
    restart_heartbeat()


# listener to heartbeat messages
def listen_heartbeat():

    server_address = ('', ports.HEARTBEAT_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_address)
    s.listen()
    print('Listening to Heartbeat on Port: {} '.format(ports.HEARTBEAT_PORT))
    while True:
        connection, server_address = s.accept()  # Wait for a connection
        heartbeat_msg = connection.recv(1024)
        heartbeat_msg = heartbeat_msg.decode()
        logging.info(f'Listening Heartbeat: received Heartbeat from: {server_address}')
        #print('Listening Heartbeat: received Heartbeat from: {} '.format(server_address))
        if heartbeat_msg:
            logging.info(f'Listening Heartbeat: sending Heartbeat back to: {server_address}')
            #print('Listening Heartbeat: sending Heartbeat back to: {} '.format(server_address))
            connection.sendall(heartbeat_msg.encode())


# function to restart heartbeat when needed
def restart_heartbeat():
    if server_data.isReplicaUpdated:
        server_data.isReplicaUpdated = False
        # if leader crashed start election
        if server_data.LEADER_CRASH:
            server_data.LEADER_CRASH = False
            print('Starting Leader Election')
            leader_election.start_leader_election(multicast_data.SERVER_LIST, server_data.SERVER_IP)
        server_data.HEARTBEAT_RUNNING = True
        thread_helper.newThread(start_heartbeat, ())
