'''
Jay Derderian
CS 594

Server module. Also runs main application (app.py).
'''

import socket, select
from app import IRC_Application, Chatroom

# Constants
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

def server():
    '''
    Main IRC server method. Instantiates a virtual server and 
    handles sending and receving messages, as well as the main 
    IRC application itself.
    '''
    print('\n***starting server***')

    host = socket.gethostname()  # host & port info
    port = PORT    

    print('\nestablishing connection...')
    # Create a new socket using IPv4 address familty (AF_INET),
    # and TCP protocol (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(host, port)
        print(f'...bound at host:{host}, port:{port}...')

        print('...listening...')
        s.listen(CLIENT_MAX)       # how many clients do we need to listen for?
        SOCKETS.append(s)          # keep track of our sockets                        
        
        # main communication loop
        while True:
            # retrieve all sockets that have been read
            read_sock, write_sock, err_sock = select.select(SOCKETS) 
            
            # iterate through read_sock 
            for notified in read_sock:    
                # initial client connection            
                if notified == s:         
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
                    message = notified.recv(BUFFER_MAX).decode()      
                    
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
                        SOCKETS.remove(notified)
                        CLIENTS.pop(notified)
                        s.close()
                        break
                    else:
                        ...
                        '''
                        Handle message parsing here...
                        '''




if __name__ == '__main__':
    server()