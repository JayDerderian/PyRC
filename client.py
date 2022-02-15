'''
Jay Derderian
CS 594

Client module. 

Handles front end of client application, user message input, 
and communicates with the server.
'''

import logging
import socket
from threading import Thread

from ui.ui import GUI
from ui.cli import CLI
from info import APP_INFO, CLIENT_COMMANDS


# Constants
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048

TEXT_UI = CLI()
UI = GUI()

CLIENT_INFO = {
    "Name": '',       # client user name
    "Address": ADDR,  # (host, port)
    "Server": ''      # connected server info
}

# Debugging stuff. Set DEBUG to true to activate logging.
DEBUG = False
if DEBUG:
    # start a log file for debugging
    logging.basicConfig(filename='IRC_Client.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')


#----------------------------------START UP-----------------------------------------#

# display welcome message
TEXT_UI.app_info(APP_INFO)
# get the username
CLIENT_INFO["Name"] = input('Enter username > ')

# Create a new socket using IPv4 address familty (AF_INET) and TCP protocol (SOCK_STREAM)
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# attempt to contact server
print('\nConnecting to server...')    
try:
    # send initial message (the username) to server
    SOCKET.connect(CLIENT_INFO['Address'])
    if DEBUG:
        logging.info(f'Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}')
    print(f'...Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
except:
    print('...Could not connect!')
    if DEBUG:
        logging.info(f'Could not connect to server! \nSocket: {SOCKET}')
    SOCKET.close()


#-------------------------------CLIENT METHODS--------------------------------------#


# display available commands
def show_commands():
    ''''
    display available commands and how to join/leave rooms 
    '''
    for key in CLIENT_COMMANDS:
        print(CLIENT_COMMANDS[key])


# messaging functionality
def message():
    '''
    handles client messages
    '''
    while True:
        '''
        NOTE: should display current room here. messages should by default
        go to the room the user is currently in, rather than having to specify
        it via command line syntax, unless joining, leaving, or listing members
        in that room.
        '''
        # get message from user
        message = input(f'{CLIENT_INFO["Name"]} > ')
        # display local help menu
        if message.split()[0]=='/help':
            show_commands()
        # exit
        elif message.split()[0] == '/quit':
            print('\n***Disconnecting!***')
            if DEBUG:
                logging.info('Disconnecting from server!')
            SOCKET.close()
        else:
            SOCKET.send(message.encode('ascii'))
        if DEBUG:
            logging.info(f'Sending message: {message}')


# main client program
def run_client():
    '''
    main client method for application. 
    handles message I/O and shuts down if a server disconnects.
    '''
    # main communication loop
    while True:
        try:
            # listen for messages from the server
            # FORMAT <user_name> #room_name : <message>
            message = SOCKET.recv(BUFFER_MAX).decode('ascii')
            # case where it's our first connection
            if message == 'Connected to server':
                if DEBUG:
                    logging.info(f'Connected to server!')
                # send user name as the first message.
                SOCKET.send(CLIENT_INFO["Name"].encode('ascii'))
            # otherwise its some other message
            else:
                if DEBUG:
                    logging.info(f'Received a message: {message}')
                # display(message)
                print(message)
        # case where the server shuts down
        except:
            if DEBUG:
                logging.info('Closing connection...')
            # display('SERVER OFFLINE! Closing connection...')
            print('\nSERVER OFFLINE! Closing connection...')
            SOCKET.close() 
            break


# message parser to use with CLI
def display(fg:str, bg:str, message:str):
    '''
    this parses a message string and applies the CLI to individual elements.

    fg = foreground color
    bg = background color
    message = str

    from app.message_broadcast():
        f'{room.name} : {name} > {message}'
    
    room.name and name should be separate colors

    room = message.split()[0]
    user_name = message.split()[1]
    col = message.split()[2]
    mes = message.split()[3]
    '''
    ...


#----------------------------------------------------------------------------#

# driver code. this uses two separate threads to run the 
# receiving of messages and one for writing.
receive_thread = Thread(target=run_client)
write_thread = Thread(target=message)
receive_thread.start()
write_thread.start()