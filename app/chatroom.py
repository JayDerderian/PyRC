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
        # Key is the user name (str), value is their socket() object 
        '''NOTE: make value User() objects?'''
        self.clients = {}  

    # returns True if a given user is in this room
    def has_user(self, user_name):
        return True if user_name in self.clients.keys() else False 

    # Adds a new client to a chatroom and notifies clients in that room
    def add_new_client_to_room(self, new_user):
        '''
        add a new client. key is their username, value is the User() object

        parameters
        ------------
        - new_user = User() object
        '''
        if self.debug:
            print(f'\nchatroom.add_new_client_to_room() - Adding {new_user.name} to {self.name}...')
            logging.info(f'chatroom.add_new_client_to_room() \nAdding: {new_user.name} \nsocket: {new_user.socket}\n')
        # add the client
        self.clients[new_user.name] = new_user
        new_user.curr_room = self.name
        return f"{new_user.name} has joined the room!"
        
    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_room(self, user):
        '''
        remove a client from a chatroom. does not update curr_name field!

        parameters
        -----------
        - client_name = '' (client to remove)
        '''
        if self.debug:
            print(f'\nchatroom.remove_new_client() - Removing {user.name} from {self.name}...')
            logging.info(f'chatroom.remove_new_client() \nRemoving {user.name} from {self.name}...\n')
        # delete the client
        del self.clients[user.name]
        return f"{user.name} has left the room!"

    # returns a list of current users in this room as a string.
    def list_users_in_room(self):
        return list([key for key in self.clients])
