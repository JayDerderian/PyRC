'''
chatroom class module.
'''

class Chatroom:

    def __init__(self, room_name):
        
        self.name = room_name
        # A dictionary of clients 
        # Key is the user name and the value is their socket() object 
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
    def list_clients_in_room(self):
        return list([key for key in self.clients])


# Broadcast a message to all clients in a given room
def message_broadcast(room, sender_name, message):
    '''
    sends a message to all the users in a Chatroom() instance

    parameters
    -----------
    - room = Chatroom() object
    - sender_name = senders name (str)
    - message = message string
    - sender_socket = sender's socket() object
    '''
    # Display message
    print(f'{room.name} {sender_name} > {message}\n')
    # Send the message to all clients in this room *except* the one that sent the messaage
    for client in room.clients:
        if client != sender_name:
            room.clients[client].send(f'{room.name} {sender_name} > {message}'.encode('ascii'))