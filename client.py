'''
Jay Derderian
CS 594

Client module. Handles front end of client application, and communicates
with the server module (and chat application).

NOTE: maybe find a way to specify connection info via argparse?
      see -> https://www.networkcomputing.com/data-centers/python-network-programming-handling-socket-errors

      long term goal: connect over internet, not just local host!
'''

import socket, select
from sys import stdin, stdout

from cli import CLI
from info import APP_INFO, CLIENT_COMMANDS


# Constants
UI = CLI()
HOST = socket.gethostname()
PORT = 5050
BUFFER_MAX = 2048
SOCKETS = []


# client class. instantiate with each new session
class Client:
    def __init__(self, name, host, port, debug=False):

        self.debug = debug          # debugger flag

        self.name = name            # client name, host, and port
        self.host = host
        self.port = port

        self.menu = CLIENT_COMMANDS # list of client commands
        self.UI = CLI()             # UI instance attached to this client

        self.messages = {}          # a dictionary of pm's. 
                                    # key is user that sent it, value is the message
    
    @classmethod
    def from_input(cls, server_socket):
        return(input(f'Enter username: '),
               HOST, 
               PORT,
               server_socket
        )

    def input_prompt(self):
        stdout.write(f'{self.name} > ')
        stdout.flush()


    def show_commands(self):
        ''''
        Display available commands and how to join/leave rooms 
        '''
        for key in self.menu:
            print(self.menu[key])
 

    # main client program
    def client(self, debug=False):
        '''
        main client method for application. handles messages and
        shuts down if a server disconnects.
        '''

        # display welcome message
        self.UI.client_info(APP_INFO)

        # get the username
        user = input('Enter username: ') 

        '''
        NOTE: specify local host or internet connection here?
        '''                     

        # Create a new socket using IPv4 address familty (AF_INET),
        # and TCP protocol (SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                
            # attempt to contact server
            print(f'\nConnecting to server...')    
            try:
                # send initial message to server with username
                s.connect((self.host, self.port))
                s.send(user.encode())
                print(f'...Connected to server at host: {self.host}, port: {self.port}')  
            except s.error as e:
                print(self.UI.error_messages('Could not connect!'))
                print(e)

            # main communication loop
            while True:

                # check stdin for client messages and server socket for server messages
                '''NOTE: Is adding stdn to SOCKETS causing issues? 
                         Need a way to check for text input from the user!
                '''
                SOCKETS = [stdin, s]  
                read_sock = select.select(SOCKETS, [], [])[0]

                # read each socket
                for notified in read_sock:
                    # messages from the server
                    if notified == s:
                        message = s.recv(s.BUFFER_MAX).decode()
                        # if the server shuts down, then message will be an empty string.
                        if not message:
                            print(f'\n***Server Disconnected!***')
                            print(f'\nshutting down...\n')
                            s.shutdown(2)
                            s.close()
                            exit()
                        # erase current line and show message, then display
                        # input prompt for client.
                        stdout.write('\r')
                        stdout.flush()
                        '''
                        NOTE: parse and encode message with UI here. 
                              look at app.message_parse() and utilize something similar to
                              assist with UI color selection.
                        '''
                        stdout.write(message)

                        self.input_prompt(user)

                    # get user input and send a message
                    else:
                        message = stdin.readline()
                        s.send(message.encode())
                        self.input_prompt()



if __name__ == '__main__':
    c = Client(name="Client", 
               host=HOST, 
               port=PORT)
    c.client()
