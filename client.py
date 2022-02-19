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

from ui.cli import CLI
from info import APP_INFO, CLIENT_COMMANDS


# Constants
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048

TEXT_UI = CLI()

CLIENT_INFO = {
    "Name": '',          # client user name
    "Address": ADDR,     # (host, port)
    "Current Room": ''   # current room. used for simplifying commands.
}

# Debugging stuff. Set DEBUG to true to activate logging.
DEBUG = True
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
        logging.info(f'client.py \nConnected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
    print(f'...Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
except:
    print('...Could not connect!')
    if DEBUG:
        logging.info(f'client.py \nCould not connect to server! \nSocket: {SOCKET}\n')
    SOCKET.close()


#-------------------------------CLIENT METHODS--------------------------------------#


# display available commands
def show_commands():
    ''''
    display available commands and how to join/leave rooms 
    '''
    # for key in CLIENT_COMMANDS:
    #     print(CLIENT_COMMANDS[key])
    return print("Not ready yet!\n")


# messaging functionality
def message():
    '''
    handles client messages
    '''
    while True:
        # get message from user. 
        '''NOTE: display() will provide a wrapper here when it's ready'''
        # message = message = input(f'{CLIENT_INFO["Current Room"]} {CLIENT_INFO["Name"]} > ')
        message = input(f'{CLIENT_INFO["Name"]} > ')

        # display local help menu
        if message.split()[0]=='/help':
            show_commands()
        # disconnect from server and exit application.
        elif message.split()[0] == '/quit':
            print('\n***Disconnecting!***')
            if DEBUG:
                logging.info(f'client.message() \nCommand used: {message.split()[0]} \nDisconnecting from server!\n')
            SOCKET.shutdown(2)
            SOCKET.close()
        # send to server
        else:
            SOCKET.send(message.encode('ascii'))
            if DEBUG:
                logging.info(f'client.message() \nSending message: {message}\n')

# main client program
def run_client():
    '''
    main client method for application. 
    handles message I/O and shuts down if a server disconnects.

    NOTE: maybe switch back to a try/except block soon?
    '''
    # main communication loop
    while True:
        # listen for messages from the server
        message = SOCKET.recv(BUFFER_MAX).decode('ascii')
        if DEBUG:
            logging.info(f'client.run_client() \nMessage from server: {message}\n')

        # case where it's our first connection
        if message == 'Connected to server':
            if DEBUG:
                logging.info('client.run_client() \nConnected to server!\n')
            # send user name as the first message.
            SOCKET.send(CLIENT_INFO["Name"].encode('ascii'))

        # case where the server shuts down
        elif not message:
            if DEBUG:
                logging.info('client.run_client() \nSERVER OFFLINE! Closing connection...\n')
            # display('SERVER OFFLINE! Closing connection...')
            print('\nSERVER OFFLINE! Closing connection...')
            SOCKET.close() 
            break

        # otherwise its some other message
        else:
            # user must be in same room as any other client to talk to them,
            # so we save the room info from the message to aid with the
            # input prompt. Try to only do this when we need to. 
            if message.split()[0] != CLIENT_INFO['Current Room']:
                CLIENT_INFO["Current Room"] = message.split()[0]
            # display(message)
            '''NOTE: is this interferring with the write thread's input prompt?
            for some reason messages from the server sort of over-lap with the text
            from the input prompt.'''
            print(message)

# message parser to use with CLI
def display(message):
    '''
    this parses a message string and applies the CLI to individual elements.

    parameters
    ------------
    - message = message string
    '''
    return TEXT_UI.add_colors(message)


#------------------------------------------------------------------------------------------#

# driver code. 
# this uses two separate threads: one for receiving messages, and one for writing.
rt = Thread(name='receive thread', target=run_client)
wt = Thread(name='write thread', target=message)
rt.start()
wt.start()