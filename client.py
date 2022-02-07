'''
Jay Derderian
CS 594

Client module. Handles front end of client application, and communicates
with the server module (and chat application).
'''

import socket, select
from cli import CLI
from sys import stdin, stdout

# Constants
UI = CLI()
HOST = socket.gethostname()
PORT = 5050
SOCKETS = []


# User input
def input_prompt(user):
    stdout.write(f'{UI.fg.lightblue} {user} > ')
    stdout.flush()


# main client method
def client():
    '''
    main client method for application. handles messages and
    shuts down if a server disconnects.
    '''
    # get the username
    user = input(f'{UI.bg.lightgrey}Enter username:{UI.fg.black}')                      

    # Create a new socket using IPv4 address familty (AF_INET),
    # and TCP protocol (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
        # create server socket and connect
        print(f'\n{UI.bg.black}Connecting to server...{UI.fg.blue}')    
        server = socket.socket()
        server.connect((HOST, PORT))
        print(f'{UI.bg.black}...Connected to server at host: {HOST}, port: {PORT}{UI.fg.lightblue}')

        # send initial message to server with username
        server.send(user.encode())           

        # main communication loop
        while True:

            # check stdin for client messages and server socket for server messages
            SOCKETS = [stdin, s]  
            read_sock, write_sock, err_sock = select.select(SOCKETS)

            # read each socket
            for notified in read_sock:
                # messages from the server
                if notified == s:
                    message = s.recv(server.BUFFER_MAX).decode()
                    # if the server shuts down, then message will be an empty string.
                    if not message:
                        print(f'{UI.bg.black}\n***Server Disconnected!***{UI.fg.red}')
                        print(f'{UI.bg.black}\nshutting down...{UI.fg.red}')
                        s.shutdown(2)
                        s.close()
                        exit()
                    # erase current line and show message, then display
                    # input prompt for client.
                    stdout.write('\r')
                    stdout.flush()
                    stdout.write(message)
                    input_prompt(user)

                # get user input and send a message
                else:
                    message = stdin.readline()
                    s.send(message.encode())
                    input_prompt()



if __name__ == '__main__':
    client()


#-----------------------------------------------------------------------------------------------------------#

'''
NOTE: Work the functions above into the class below, and create a 
      separate run_client() method that instantiates the Client() object. 
'''

'''
if __name__ == '__main__':
    c = Client(host=HOST, port=PORT)
    c.server()
'''


# client class. instantiate with each new session
class Client:
    def __init__(self, name, host, port, server_socket):
        self.name = name
        self.host = host
        self.port = port
        self.server_socket = server_socket
    
    @classmethod
    def from_input(cls, server_socket):
        return(input(f'{UI.bg.lightgrey} Enter username: {UI.fg.darkgrey} '),
               HOST, 
               PORT,
               server_socket
        )

    def input_prompt(self):
        stdout.write(f'{UI.fg.blue} {self.name} > ')
        stdout.flush()

    # startup message
    def startup_message(self):
        welcome = f'{UI.bg.lightgrey}'

    # main client program
    def client(self):
        '''
        main client method for application. handles messages and
        shuts down if a server disconnects.
        '''
        # get the username
        user = input(f'{UI.bg.lightgrey}Enter username: {UI.fg.black}')                      

        # Create a new socket using IPv4 address familty (AF_INET),
        # and TCP protocol (SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                
            # create server socket and connect
            print(f'\n{UI.bg.black}Connecting to server...{UI.fg.blue}')    
            server = socket.socket()
            server.connect((HOST, PORT))
            print(f'{UI.bg.black}...Connected to server at host: {HOST}, port: {PORT}{UI.fg.lightblue}')

            # send initial message to server with username
            server.send(user.encode())           

            # main communication loop
            while True:

                # check stdin for client messages and server socket for server messages
                SOCKETS = [stdin, s]  
                read_sock, write_sock, err_sock = select.select(SOCKETS)

                # read each socket
                for notified in read_sock:
                    # messages from the server
                    if notified == s:
                        message = s.recv(server.BUFFER_MAX).decode()
                        # if the server shuts down, then message will be an empty string.
                        if not message:
                            print(f'{UI.bg.black}\n***Server Disconnected!***{UI.fg.red}')
                            print(f'{UI.bg.black}\nshutting down...{UI.fg.red}')
                            s.shutdown(2)
                            s.close()
                            exit()
                        # erase current line and show message, then display
                        # input prompt for client.
                        stdout.write('\r')
                        stdout.flush()
                        stdout.write(message)
                        self.input_prompt(user)

                    # get user input and send a message
                    else:
                        message = stdin.readline()
                        s.send(message.encode())
                        self.input_prompt()