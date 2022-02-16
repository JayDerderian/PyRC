'''
chatroom class module.
'''

class Chatroom:
    '''
    chatroom class. keeps track of clients in a dictionary (key = username, value = user_socket)
    '''

    def __init__(self, room_name):
        
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

        self.clients[client_name] = new_socket
    
        return f"{client_name} has joined the room!\n"
        
    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_room(self, client_name, client_socket):
        print(f'\nremoving {client_name} from {self.name}')

        self.clients.pop(client_name)

        return f"{client_name} has left the room!\n"

    # returns a list of current users in this room as a string.
    def list_users_in_room(self):
        return list([key for key in self.clients])
