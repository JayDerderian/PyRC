'''
chatroom class module.
'''

import logging

# Debugging stuff. Set DEBUG to True to activate logging.
DEBUG = True
if DEBUG:
    # start a log file for debugging
    logging.basicConfig(filename='IRC_Chatroom.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')

class Chatroom:
    '''
    chatroom class. keeps track of clients in a dictionary (key = username, value = user_socket)
    '''

    def __init__(self, room_name, debug=False):
        self.debug = debug

        self.name = room_name
        # A dictionary of clients 
        # Key is the user name, value is their socket() object 
        self.clients = {}  

    # returns True if a given user is in this room
    def has_user(self, user_name):
        return True if user_name in self.clients.keys() else False 

    # Adds a new client to a chatroom and notifies clients in that room
    def add_new_client_to_room(self, client_name, new_socket):
        print(f'\nadding {client_name} to {self.name}')
        logging.info(f'chatroom.add_new_client_to_room() \nadding: {client_name} \nsocket: {new_socket}')

        self.clients[client_name] = new_socket
    
        return f"{client_name} has joined the room!"
        
    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_room(self, client_name):
        print(f'chatroom.remove_new_client() \nremoving {client_name} from {self.name}')
        logging.info(f'chatroom.remove_new_client() \nremoving {client_name} from {self.name}')

        del self.clients[client_name]

        return f"{client_name} has left the room!"

    # returns a list of current users in this room as a string.
    def list_users_in_room(self):
        return list([key for key in self.clients])
