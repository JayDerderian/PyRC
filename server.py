'''
Jay Derderian
CS 594

Server module. Also runs main IRC application (app.py).
'''

import socket, select
from app import IRC_Application, Chatroom

# Constants
HOST = socket.gethostname()  # host & port info
PORT = 5050
SOCKETS = []
CLIENTS = {}
BUFFER_MAX = 2048
CLIENT_MAX = 10

# Application and Chatroom instances
# irc = IRC_Application()
# default_room = Chatroom(name=Chatrooms.DEFAULT_NAME)
# irc.rooms[Chatrooms.DEFAULT_NAME] = default_room

'''
Add irc_instance and default chat room once they're ready
'''
class Server:

    def __init__(self, host, port, debug=False):
        self.debug = debug

        self.host = host
        self.port = port
        self.sockets = []
        self.clients = {}
        # self.app = app


    def server():
        '''
        Main IRC server method. Instantiates a virtual server and 
        handles sending and receving messages, as well as the main 
        IRC application itself.
        '''
        print('\n***starting server***')

        print('\nestablishing connection...')
        # Create a new socket using IPv4 address familty (AF_INET),
        # and TCP protocol (SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            # intitialize server and listen for clients
            s.bind((HOST, PORT))
            print(f'...bound at host:{HOST}, port:{PORT}...')
            print('...listening...\n')
            s.listen(CLIENT_MAX)       # how many clients do we need to listen for?
            SOCKETS.append(s)          # keep track of our sockets (starting with ours!)                        
            
            # main communication loop
            while True:
                # retrieve all sockets that have been read
                read_sock = select.select(SOCKETS, [], [])[0]
                
                # iterate through read_sock 
                for recieved in read_sock:    
                    # initial client connection            
                    if recieved == s:         
                        new_client_sock, new_client_addr = s.accept()
                        # save the new client socket
                        SOCKETS.append(new_client_sock)                   
                        print(f'\n...new client connected! addr:{new_client_addr}')
                        # save username
                        user = new_client_sock.recv(BUFFER_MAX).decode() 
                        CLIENTS[new_client_sock] = user
                        '''
                        create new chatroom here using new app instance...
                        '''
                    # existing client communication (new message)
                    else:                    
                        message = recieved.recv(BUFFER_MAX).decode()      
                        if not message:
                            print("\n***all clients disconnected!***")
                            print("\nshutting down server...")
                            '''
                            shut down irc instance and remove all rooms 
                            here...
                            '''    
                            '''
                            NOTE: maybe use clear() for both lists when shutting down
                                if all users have exited?
                            '''
                            SOCKETS.remove(recieved)
                            CLIENTS.pop(recieved)
                            s.close()
                            break
                        else:
                            ...
                            '''
                            Handle message parsing here...
                            '''



if __name__ == '__main__':
    s = Server(host=HOST, port=PORT)
    s.server()