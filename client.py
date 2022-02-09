'''
Jay Derderian
CS 594

Client module. 

Handles front end of client application, user message input, 
and communicates with the server.
'''

import socket
import threading

from ui import GUI
from cli import CLI
from info import APP_INFO, CLIENT_COMMANDS


# Constants
DEBUG = False
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048

CLIENT_INFO = {
    "Name": '',       # client user name
    "Address": ADDR,  # (host, port)
    "Sockets": {},    # key = 'server', value = socket
    "Messages": {}    # key = 'sender', value = message (str)
}

TEXT = CLI()
UI = GUI()


#------------------------------------START UP------------------------------------------

# display welcome message
TEXT.app_info(APP_INFO)
# get the username
CLIENT_INFO["Name"] = input('Enter username > ')

# ****Create a new socket using IPv4 address familty (AF_INET),
#     and TCP protocol (SOCK_STREAM)****
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# attempt to contact server
print(f'\nConnecting to server...')    
try:
    # send initial message (the username) to server
    SOCKET.connect(CLIENT_INFO['Address'])
    # save our server info (even though it says client)
    CLIENT_INFO['Sockets']['Server'] = SOCKET
    print(f'...Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
except:
    print('...Could not connect!')

#-------------------------------------------------------------------------------------


# display available commands
def show_commands():
    ''''
    display available commands and how to join/leave rooms 
    '''
    for key in CLIENT_COMMANDS:
        print(CLIENT_COMMANDS[key])


# message prompt for user
def message():
    '''
    handle client messages
    '''
    while True:
        message = input(f'{CLIENT_INFO["Name"]} > ')
        '''check whether the user wants the show_commands() methods!'''
        SOCKET.send(message.encode('ascii'))


# main client program
def run_client():
    '''
    main client method for application. 
    handles message I/O and shuts down if a server disconnects.
    '''
    # main communication loop
    while True:
        # case where we first connect to server
        try:
            message = SOCKET.recv(BUFFER_MAX).decode('ascii')
            # check for connection confirmation
            if message == 'Connected to server':
                # send user name if connected
                SOCKET.send(CLIENT_INFO["Name"].encode('ascii'))
            # otherwise its some other message
            else:
                print(message)
        # case where the server shuts down
        except:
            print("SERVER SHUT DOWN")
            # might be redundant since we used 'with'
            SOCKET.close() 
            break

#----------------------------------------------------------------------------

# driver code
receive_thread = threading.Thread(target=run_client)
write_thread = threading.Thread(target=message)
receive_thread.start()
write_thread.start()
