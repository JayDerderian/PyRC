'''
Jay Derderian
CS 594

Server module. Also runs main IRC application (app.py).
'''

import socket
from threading import Thread

from app.pyrc import PyRC

# Constants
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048
CLIENT_MAX = 10
DEFAULT_ROOM_NAME = '#lobby'

# keeps track of active threads.
# key is client (socket() object), value is thread
ACTIVE_THREADS = {}

# Application instance.
APP = PyRC()  

# Server info
SERVER_INFO = {
    "Sockets": [],  # list of client_socket objects
    "Users": [],    # list of tuples (client_socket object, client_username)
}

# Debugging stuff. Set DEBUG to True to activate logging.
DEBUG = True
if DEBUG:
    import logging
    # start a log file for debugging
    logging.basicConfig(filename='PyRC_Server.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')
                        

#--------------------------------------START UP-------------------------------------------#


# Create a new socket using IPv4 address familty (AF_INET),
# and the TCP protocol (SOCK_STREAM)
print('\n***starting server***')
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET.bind(ADDR)
print(f'\n...bound at host: {ADDR[0]}, port:{ADDR[1]}...')
print('...listening...\n')
SOCKET.listen(CLIENT_MAX)              # how many clients do we need to listen for?
if DEBUG:
    logging.info(f'server.py \nSERVER STARTED \nHost: {HOST}, Port: {PORT}\n')


#-----------------------------------SERVER LOOP-----------------------------------------#


# *******************************************************************************
# TODO: add command parser? 
#       maybe introduce a way to manually shut down server while it's running?
#
# TODO: look into thread limits? how many individual user threads can a small server
#       handle?
#    
#       if __name__ == '__main__':
#           while len(ACTIVE_THREADS) > n:
#               run_server()
# ******************************************************************************

def run_server():
    '''
    runs communication loop
    '''
    while True:
        # allow clients to connect
        client, address = SOCKET.accept()
        if DEBUG:
            logging.info(f'server.run_server() \nClient connected! Address: {address}\n') 
        '''
        TODO: modify this if-statement to account whether we've reached a thread limit!
           
              if len(ACTIVE_THREADS) < n:
                  # new user
                      ...
                      etc...
        '''
        # new user!
        if client not in SERVER_INFO["Sockets"]:
            # confirm connection to new user, and broadcast to app
            if DEBUG:
                logging.info(f'server.run_server() \nSending new client connection confirmation...\n')
            client.send('Connected to server'.encode('ascii'))

            # get user name since that's the first message
            new_user = client.recv(BUFFER_MAX).decode('ascii')
            if DEBUG:
                logging.info(f'server.run_server() \nNew user - Name: {new_user},  Address:{address}\n')
                print(f'adding new socket and user name to SERVER_INFO: \nuser: {new_user} \nsocket object: {client} ')
            SERVER_INFO["Sockets"].append(client)
            # NOTE: add address to SERVER_INFO["Users"]? 
            SERVER_INFO["Users"].append((client, new_user)) # yes, i know clients are being saved twice
            print(f'...new user connected! name: {new_user}, addr: {str(address)}\n')

            # add user to instance (and default room) and update user dict
            APP.add_user(new_user, client)
            
            # create a new thread for this client to handle message I/O
            thread = Thread(target=handle, args=(client,))
            thread.start()
            # ACTIVE_THREADS[client] = Thread(target=handle, args=(client,)
            # ACTIVE_THREADS[client].start()

        # message from existing user (handled in separate thread!)
        else:
            ...

'''
NOTE: This loop operates on its own thread, and each new user gets a new thread 
      created for them when they join. 

      This is the current approach to asynchronous I/O, though it'll be worth it 
      to look into this further!
'''
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
            if DEBUG:
                logging.info(f'server.handle() \nMessage from user: {user} \nMessage: {message}\n')
                
            # parse message in app
            APP.message_parser(message, user, client)

        # case where a user disconnects
        except:
            print("\n***USER DISCONNECT***")
            # search user list for the username associated with this client
            user = find_user(client)[1]
            if DEBUG:
                logging.info(f'server.handle() \n{user} left the server! \nsocket: {str(SERVER_INFO["Sockets"].index(client))}\n')

            # remove user from APP instance
            APP.remove_user(user)
            
            # remove user info from SERVER_INFO instance, and close socket
            SERVER_INFO["Sockets"].remove(client)
            SERVER_INFO["Users"].remove((client, user))
            client.close()
            # del ACTIVE_THREADS[client]
            
            print(f'{user} left the server!\n')
            break


def find_user(client):
    '''
    finds a user_name associated with a client socket object.

    parameters
    ------------
    - client = client socket() object
    
    returns a tuple (user_socket (socket(), user_name (str)))
    '''
    user_list = SERVER_INFO["Users"]
    index = [i for i, user_list in enumerate(user_list) if user_list[0] == client]
    return SERVER_INFO["Users"][index[0]]


#----------------------------------DRIVER CODE--------------------------------------#

if __name__ == '__main__':
    run_server()