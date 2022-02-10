'''
Jay Derderian
CS 594

Server module. Also runs main IRC application (app.py).
'''

import socket
import threading
from app import IRC_Application, Chatroom

# Constants
HOST = socket.gethostname()  # host & port info
PORT = 5050
ADDR = (HOST, PORT)
BUFFER_MAX = 2048
CLIENT_MAX = 10

SERVER_INFO = {
    "Sockets": [],
    "Users": [],
    "Rooms": [],
}

# Application and Chatroom instances
# APP = IRC_Application()
# default_room = Chatroom(name=Chatrooms.DEFAULT_NAME)
# APP.rooms[Chatrooms.DEFAULT_NAME] = default_room

#-------------------------START UP----------------------------------#

# ****Create a new socket using IPv4 address familty (AF_INET),
#     and TCP protocol (SOCK_STREAM)****
print('\n***starting server***')
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET.bind(ADDR)
print(f'\n...bound at host: {ADDR[0]}, port:{ADDR[1]}...')
print('...listening...\n')
SOCKET.listen(CLIENT_MAX)              # how many clients do we need to listen for?

#-------------------------------------------------------------------#

def broadcast(message):
    '''
    NOTE: modify IRC app to do this for the room the user is in!
          this just broadcasts to *everyone*
    '''
    for client in range(len(SERVER_INFO["Sockets"])):
        SERVER_INFO["Sockets"][client].send(message)


def run_server():
    '''
    runs communication loop
    '''
    while True:
        # allow clients to connect
        client, address = SOCKET.accept()  
        # new user!
        if client not in SERVER_INFO["Sockets"]:
            # confirm connection to new user, and broadcast to app
            client.send(f'Connected to server'.encode('ascii'))

            # get user name since that's the first message
            new_user = client.recv(BUFFER_MAX).decode('ascii') 
            SERVER_INFO["Sockets"].append(client)
            SERVER_INFO["Users"].append(new_user)

            # alert new connection via the terminal
            print(f'...new user connected! name: {new_user}, addr: {str(address)}\n')

            # create a new thread for this client to handle message I/O
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        # app message parsing here?
        else:
            message = client.recv(BUFFER_MAX).decode('ascii')
            # print recieved message in terminal for now
            print(f'\n{message}')


def handle(client):
    '''
    handles when a user gets a message or leaves. 
    '''
    while True:
        try:
            message = client.recv(BUFFER_MAX)
            '''
            NOTE: parse message with IRC APP here?
            '''
            print(message)
        except:
            index = SERVER_INFO["Sockets"].index(client)
            SERVER_INFO["Sockets"].remove(client)
            user = SERVER_INFO["Users"][index]
            SERVER_INFO["Users"].remove(user)

            print(f'{user} left the server!')
            '''
            NOTE: broadcast within app to the room the user was in
            '''
            client.close()
            break


# driver code
if __name__ == '__main__':
    run_server()
