'''
Jay Derderian
CS 594

Server module. Also runs main IRC application (app.py).
'''

import socket
import threading

from app.pyrc import PyRC

# Constants
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048
CLIENT_MAX = 10
DEFAULT_ROOM_NAME = '#lobby'

# keeps track of active threads (individual users).
# key is client (socket() object), value is thread() object
ACTIVE_THREADS = {}

# Application instance.
APP = PyRC()  

# Server session info. 
# This external constant needs to be accessed by multiple threads, 
# otherwise it would be a field in the server() class
SERVER_INFO = {
    "Sockets": [],  # list of client_socket objects
    "Users": [],    # list of tuples (client_socket object, client_username)
}   

def find_user(client):
    '''
    finds a user_name associated with a client socket object.

    parameters
    ------------
    - user_name = ''
    
    returns a tuple (user_socket (socket(), user_name (str)))
    '''
    user_list = SERVER_INFO["Users"]
    index = [i for i, user_list in enumerate(user_list) if user_list[0] == client]
    return SERVER_INFO["Users"][index[0]]
    

class Server(threading.Thread):
    '''
    Class for handling everything server-related.
    '''
    def __init__(self, host, port):
        # start a new thread for this server
        threading.Thread.__init__(self)
        self.running = True
        self.host = host
        self.port = port
        self.socket = None

    def run(self):
        '''
        Initializes a new socket() object and runs communication loop
        '''
        print('\n***starting server***')

        # Create a new socket using IPv4 address familty (AF_INET),
        # and the TCP protocol (SOCK_STREAM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(ADDR)
        self.socket.listen(CLIENT_MAX)

        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, None)
        print(f'\n...bound at host: {ADDR[0]}, port:{ADDR[1]}...')
        print('...listening...\n')

        while self.running:
            try:
                # allow clients to connect
                # this is a BLOCKING process! might interfere
                # with the KeyboardInterrupt exception...
                client, address = self.socket.accept()
                # new user!
                if client not in SERVER_INFO["Sockets"]:
                    # confirm connection to new user, and broadcast to app
                    client.send('Connected to server'.encode('ascii'))

                    # get user name since that's the first message
                    new_user = client.recv(BUFFER_MAX).decode('ascii')
                    SERVER_INFO["Sockets"].append(client)
                    SERVER_INFO["Users"].append((client, new_user)) # yes, i know clients are being saved twice
                    print(f'...new user connected! name: {new_user}, addr: {str(address)}\n')

                    # add user to instance (and default room) and update user dict
                    APP.add_user(new_user, client)

                    # create a new thread for this client to handle message I/O
                    ACTIVE_THREADS[client] = threading.Thread(target=handle, args=(client,))
                    ACTIVE_THREADS[client].start()

                # message from existing user (handled in separate thread!)
                else:
                    ...
            except ConnectionResetError:
                pass
            except KeyboardInterrupt:
                self.shut_down()

    # handles server shut down
    def shut_down(self):
        '''
        shut down the server
        '''
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print("\nSERVER OFFLINE!\n")


def handle(client):
    '''
    handles individual user I/O. operates in it's own thread.
    '''
    while True:
        # case where the server recieves a message 
        # from an existing client
        try:
            message = client.recv(BUFFER_MAX).decode('ascii')
            # search user list for the username associated with this client
            user = find_user(client)[1]   
            # parse message in app
            APP.message_parser(message, user, client)

        # case where a user disconnects
        except:
            print("\n***USER DISCONNECT***")
            # search user list for the username associated with this client
            user = find_user(client)[1]
            # remove user from APP instance
            APP.remove_user(user)
            
            # remove user info from SERVER_INFO instance, and close socket
            SERVER_INFO["Sockets"].remove(client)
            SERVER_INFO["Users"].remove((client, user))
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            print(f'{user} left the server!\n')
            break


#### DRIVER CODE ####
if __name__ == '__main__':

    server = Server(host=HOST, port=PORT)
    server.run()