'''
Jay Derderian
CS 594

Client module. Handles front end of client application, and communicates
with the server module (and chat application).
'''

import socket, select
from sys import stdin, stdout


# Constants
HOST = socket.gethostname()
PORT = 5050
SOCKETS = []

# User input
def input_prompt(user):
    stdout.write(f'{user} > ')
    stdout.flush()


# main client method
def client():
    '''
    main client method for application. handles messages
    '''
    user = input('\nEnter username: ')                      

    # Create a new socket using IPv4 address familty (AF_INET),
    # and TCP protocol (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
        print('\nConnecting to server...')    # create server socket and connect
        server = socket.socket()
        server.connect((HOST, PORT))
        print(f'...Connected to server at host: {HOST}, port: {PORT}')

        server.send(user.encode())           # send initial message to server with username

        # main communication loop
        while True:
            SOCKETS = [stdin, s]  # check stdin for client messages and server socket for server messages
            read_sock, write_sock, err_sock = select.select(SOCKETS)
            # read each socket
            for notified in read_sock:
                # messages from the server
                if notified == s:
                    message = s.recv(server.BUFFER_MAX).decode()
                    # if the server shuts down, then message will be an empty string.
                    # using 'with' means we don't need to use s.close()
                    if not message:
                        print('\n***Server Disconnected!***')
                        print('\nshutting down...')
                        s.shutdown(2)
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


'''
NOTE

Work the class below into an object in the above client()
method.
'''
# client class. instantiate with each new session
class Client:
    def __init__(self, name, host, port, server_socket):
        self.name = name
        self.host = host
        self.port = port
        self.server = server_socket
    
    @classmethod
    def from_input(cls, server_socket):
        return(input('Enter username: '),
               HOST, 
               PORT,
               server_socket
        )

    def user_input(self):
        stdout.write(f'{self.name} > ')
        stdout.flush()