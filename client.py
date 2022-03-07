'''
Jay Derderian
CS 594

Client module. 

Handles front end of client application, user message input, 
and communicates with the server.
'''

import socket
import threading

from ui.tui import (
    TUI, supports_color, app_info
)
from info import APP_INFO, CLIENT_COMMANDS

# Constants
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048

CLIENT_INFO = {
    "Name": '',          # client user name
    "Address": ADDR,     # (host, port)
    "Current Room": ''   # current room. used for simplifying commands.
}

SUPPORTS_COLOR = False
if supports_color():
    TEXT_UI = TUI()
    SUPPORTS_COLOR = True

# display available commands
def show_commands():
    ''''
    display available commands
    '''
    for key in CLIENT_COMMANDS:
        print(CLIENT_COMMANDS[key])

# messaging functionality
def message():
    '''
    handles client messages. runs in its own thread.
    '''
    while True:
        # get message from user. 
        message = input()

        # display local help menu
        if message.split()[0]=='/help':
            show_commands()
        
        # disconnect from server and exit application.
        elif message.split()[0] == '/quit':
            print('\n***Disconnecting!***')
            SOCKET.shutdown(socket.SHUT_RDWR)
            SOCKET.close()
    
        # send to server
        else:
            SOCKET.send(message.encode('ascii'))


# main client program
def run_client():
    '''
    main client method for application. 
    handles message I/O and shuts down if a server disconnects.

    runs in its own thread.
    '''
    # main communication loop
    while True:
        try: 
            # listen for messages from the server
            message = SOCKET.recv(BUFFER_MAX).decode('ascii')

            # case where it's our first connection
            if message == 'Connected to server':
                # send user name as the first message.
                SOCKET.send(CLIENT_INFO["Name"].encode('ascii'))

            # case where the server shuts down
            elif not message:
                # if SUPPORTS_COLOR:
                #     display('SERVER OFFLINE! Closing connection...')
                # else:
                #     print('\nSERVER OFFLINE! Closing connection...')
                print('\nSERVER OFFLINE! Closing connection...')
                SOCKET.close() 
                break
            # otherwise its some other message
            else:
                # if SUPPORTS_COLOR:
                #     display()
                # else:
                #     print(message)
                print(message)

        # case where there's a problem with the server
        except ConnectionResetError:
            pass

# message parser to use with TUI
def display(message):
    '''
    this parses a message string *received* from the server,
    parses it for the room name and user name, and adds an 
    individual color to each.

    parameters
    ------------
    - message = message string
    
    TODO:
        Go through PyRC.py and find all the places message_broadcast() is called,
        and what's being sent to it.

        Need to differentiate a way from a message sent from a chatroom vs dm or whisper!

        Keep a list of rooms client side and randomly assign colors on this end??
    '''
    ...


### DRIVER CODE ###

# driver code. 
if __name__ == '__main__':

    ### START UP ###

    # display welcome message
    app_info(APP_INFO)

    # get the username
    CLIENT_INFO["Name"] = input('Enter username > ')

    # Create a new socket using IPv4 address familty (AF_INET) and TCP protocol (SOCK_STREAM)
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # attempt to contact server
    print('\nConnecting to server...')    
    try:
        # send initial message (the username) to server
        SOCKET.connect(CLIENT_INFO['Address'])
        print(f'...Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
        
        ### MAIN THREADS ###
        '''
        TODO:
            Find a way to handle when one of these shuts down while the other is going. 
            Need to find some sort of thread shut down exception that will shut down
            the other thread if one of them suddenly shuts down.
        '''
        # this uses two separate threads: one for receiving messages, and one for writing.
        rt = threading.Thread(name='receive thread', target=run_client)
        wt = threading.Thread(name='write thread', target=message)
        rt.start()
        wt.start()

        # NEED TO CATCH THREAD EXCEPTIONS HERE-ISH

    except:
        print('...Could not connect!')
        SOCKET.close()
        exit()
