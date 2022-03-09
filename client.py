'''
Jay Derderian
CS 594

Client module. 

Handles front end of client application, user message input, and communicates with the server.
'''
import os
import socket
import threading

from ui.tui import (
    TUI, supports_color, app_info
)
from info import APP_INFO, CLIENT_COMMANDS


### Constants ###
HOST = socket.gethostname()
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048
CLIENT_INFO = {
    "Name": '',          # client user name
    "Address": ADDR,     # (host, port)
}

#### TUI ####
SUPPORTS_COLOR = False
if supports_color():
    os.system('color')
    TEXT_UI = TUI()
    SUPPORTS_COLOR = True

# messaging functionality
def message():
    '''
    handles client messages sent to the server from the client. 
    runs in its own thread.
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
            exit()

        # clear terminal output
        elif message.split()[0] == '/clear':
            clear()

        # send to server
        else:
            # assign a color to this room if we're joining a new one
            if SUPPORTS_COLOR and message.split()[0] == '/join':
                for word in message.split():
                    if word[0] == '#':
                        TEXT_UI.assign_colors(word)
            SOCKET.send(message.encode('ascii'))

# main client program
def run_client():
    '''
    main client method for application. handles messages from the server

    runs in its own thread.
    '''
    # main communication loop
    while True:
        try: 
            # listen for messages from the server
            message = SOCKET.recv(BUFFER_MAX).decode('ascii')

            # case where it's our first connection
            if message == 'Connected to server':
                if SUPPORTS_COLOR:
                    TEXT_UI.assign_colors('#lobby')
                # send user name as the first message.
                SOCKET.send(CLIENT_INFO["Name"].encode('ascii'))

            # case where the server shuts down
            elif not message:
                if SUPPORTS_COLOR:
                    TEXT_UI.shut_down_message('SERVER OFFLINE! Closing connection...')
                else:
                    print('\nSERVER OFFLINE! Closing connection...')
                SOCKET.close()
                break

            # otherwise its some other message
            else:
                # get any room names, assign colors as needed, then display
                if SUPPORTS_COLOR:
                    TEXT_UI.display(message)
                else:
                    print(message + '\n')

        # case where there's a problem with the server
        except ConnectionResetError:
            pass
        # case where we have a socket error
        except socket.error:
            if SUPPORTS_COLOR:
                TEXT_UI.shut_down_message('SERVER OFFLINE! Closing connection...')
            else:
                print('\nSERVER OFFLINE! Closing connection...')
            SOCKET.close()
            break

# display available commands
def show_commands():
    ''''
    display available commands
    '''
    for key in CLIENT_COMMANDS:
        print(CLIENT_COMMANDS[key])

# clear terminal
def clear():
    '''
    clears terminal output
    '''
    os.system('cls' if os.name=='nt' else 'clear')


######## DRIVER CODE #########
if __name__ == '__main__':

    ### START UP ###
    app_info(APP_INFO)                                 # display welcome message
    CLIENT_INFO["Name"] = input('Enter username > ')   # get the username

    # Create a new socket using IPv4 address familty (AF_INET) 
    # and TCP protocol (SOCK_STREAM)
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # attempt to contact server
    print('\nConnecting to server...')    
    try:
        # send initial message (the username) to server
        SOCKET.connect(CLIENT_INFO['Address'])
        if SUPPORTS_COLOR:
            TEXT_UI.connected_message('Connected!')
        else:
            print(f'...Connected to server at host: {CLIENT_INFO["Address"][0]}, port: {CLIENT_INFO["Address"][1]}\n')
        
        ### MAIN THREADS ###
        rt = threading.Thread(name='receive thread', target=run_client)
        wt = threading.Thread(name='write thread', target=message)
        rt.start()
        wt.start()
        # this continually checks to make sure each thread is running. 
        # its janky af and probably really silly, but it seems to 
        # handle thread exceptions when the client shuts down using the
        # /quit command
        try:
            while rt.is_alive() and wt.is_alive():
                pass
        except threading.ThreadError:
            exit()

    except:
        if SUPPORTS_COLOR:
            TEXT_UI.error_messages('Unable to connect!')
        else:
            print('...Unable to connect!')
        try:
            SOCKET.shutdown(socket.SHUT_RDWR)
            SOCKET.close()
            exit()
        except:
            exit()