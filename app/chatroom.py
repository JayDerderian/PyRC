'''
chatroom class module.
'''

import logging

class Chatroom:
    '''
    chatroom class. keeps track of clients in a dictionary (key = username, value = user_socket)
    '''

    def __init__(self, room_name, debug=False):
        self.debug = debug
        if self.debug:
            logging.basicConfig(filename='IRC_Chatroom.log', 
                    filemode='w', 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')

        self.name = room_name
        # A dictionary of clients 
        # Key is the user name (str), value is the User() object 
        self.clients = {}  

    # returns True if a given user is in this room
    def has_user(self, user_name):
        return True if user_name in self.clients.keys() else False

    # returns a list of users in this room:
    def get_users(self):
        user_list = list(self.clients.keys())
        return " ".join(user_list) 

    # Adds a new client to a chatroom and notifies clients in that room
    def add_new_client_to_room(self, new_user):
        '''
        add a new client. key is their username, value is the User() object

        updates User() object fields curr_room and curr_rooms if this room 
        hasn't been visited by the user yet.

        parameters
        ------------
        - new_user = User() object
        '''
        if self.debug:
            logging.info(f'chatroom.add_new_client_to_room() \nAdding: {new_user.name} \nsocket: {new_user.socket}\n')
        # add the client if they're not already here
        if new_user.name not in self.clients.keys():
            self.clients[new_user.name] = new_user
            if self.name not in new_user.curr_rooms:
                new_user.curr_rooms.append(self.name)
        else:
            new_user.send(f'Error: you are already in {self.name}!'.encode('ascii'))
        
    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_room(self, user):
        '''
        remove a client from a chatroom. 
        does not modify users curr_room list!

        parameters
        -----------
        - user = '' (client to remove)
        '''
        if self.debug:
            logging.info(f'chatroom.remove_client_from_room() \nRemoving {user} from {self.name}...\n')
        if user in self.clients.keys():
            self.clients.pop(user)
        else:
            print(f'ERROR: {user} is not in {self.name}!')
            if self.debug:
                logging.error(f'chatroom.remove_client_from_room() \nERROR: {user} was not in room {self.name}!')

    # send a message to all users in chatroom
    def message_all_clients(self, sender, message):
        '''
        send a message to all clients in the room. 
        accounts for whether a client has blocked sender.

        parameters
        ------------
        - sender = ''
        - message = ''
        '''
        if len(self.clients) > 0:
            for user in self.clients:
                if self.clients[user].has_blocked(sender):
                    continue
                self.clients[user].send(message.encode('ascii'))
        else:
            ...