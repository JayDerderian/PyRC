'''
Jay Derderian
CS 594

Application module - the core functionality of the IRC Chat program.

This handles tracking of clients and their associated sockets, sending
and recieving messages, message parsing, and other neccessary functionality.

There is also built-in debugging functionality using logs. 
Set DEBUG to true to turn on logging system.
'''


DEFAULT_ROOM_NAME = '#lobby'

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


# The container that has rooms, which have lists of clients
class IRC_App:
    '''
    The main IRC application. One default room - #lobby - is created when
    this class is instantiated. Irc_App() also keeps tracks of current users 
    and their socket info.

    Irc_App().message_parser(message:str) is the main point of entry for this
    application. All message strings recieved from the client should be sent 
    through here.
    '''
    def __init__(self, debug=False):
        # Debuggin' stuff
        self.debug = debug
        # Dictionary of active rooms. Key is room name, value is the Chatroom() object. 
        # #lobby room is always present by default, even if its empty.
        self.rooms = {}
        self.rooms[DEFAULT_ROOM_NAME] = Chatroom(room_name=DEFAULT_ROOM_NAME)  
        # Dictionary of active users
        # Key is username, value is User() object
        self.users = {}

    # add a new user to the instance
    def add_user(self, user_name, new_user_socket):
        if user_name not in self.users.keys():
            self.users[user_name] = User(name=user_name, 
                                         socket=new_user_socket)
        else:
            print(f'{user_name} is already in the server!')

    # remove a user from the instance
    def remove_user(self, user_name):
        if user_name in self.users.keys():
            del self.users[user_name]
        else:
            print(f'{user_name} is not in the server!')
    
    # get a list of all active users
    def get_all_users(self):
        '''
        returns a list[str] of all active users in the instance.
        '''
        return list(self.users.keys())

    # returns a list of active rooms
    def list_all_rooms(self):
        '''
        returns a list of all active rooms.
        '''
        return list(self.rooms.keys())
    
    # gets the current room a user is in
    def get_current_room(self, user_name):
        '''
        returns the room name a user is currently in.
        '''
        for room in self.rooms:
            if self.rooms[room].has_user(user_name):
                return self.rooms[room].name
    
    # get a user's connection info
    def get_connection_info(self, user_name):
        '''
        show current client's name, and socket info.
        returns a tuple with the user_name and socket() object
        '''
        if user_name in self.users.keys():
            return (user_name, self.users[user_name])
        else:
            print(f'{user_name} not in instance!')

    # Check if the room name begins with '#', check if user is already in the room,
    # create the room if it does not exist, then join the room the user specified
    def join_room(self, room_to_join, sender_name, sender_socket):
        '''
        join or create a new Chatroom() instance

        parameters
        --------------
        - room_to_join = '#room_name'
        - sender_name = ''
        - sender_socket = sender socket() object

        '''
        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            if self.debug:
                print(f'Creating and joining {room_to_join}...')
            self.create_room(room_to_join, sender_name, sender_socket)
        # Case where it DOES already exist
        else:
            if self.debug:
                print(f'Joining {room_to_join}...')
            self.rooms[room_to_join].add_client_to_room(sender_name, sender_socket)

    # Create a new Chatroom, add the room to the room list, and add the client to the chatroom
    # A room cannot exist without a client, so one must be supplied
    def create_room(self, room_to_join, sender_name, sender_socket):
        '''
        creates a new Chatroom() instance. 
        dont use directly! should only be called by self.join_room()

        parameters
        -------------
        - room_to_join = '#room_name
        - sender_name = ''
        - sender_socket = sender socket() object
        '''
        self.rooms[room_to_join] = Chatroom(room_name=room_to_join)
        self.rooms[room_to_join].add_new_client_to_room(sender_name, sender_socket)

    # Check if the room exists, check if user is in the room,
    # remove user from room and delete room if it is empty
    def leave_room(self, room_to_leave, sender_name, sender_socket):
        '''
        leave a Chatroom() instance. will remove room if it's empty.

        parameters
        -------------
        - room_to_leave = '' (key for app.rooms dict)
        - sender_socket = sender socket() objet
        - sender_name = ''
        '''
        # case where room doesn't exist
        if room_to_leave not in self.rooms.keys():
            sender_socket.send(f'Error: {room_to_leave} does not exist\n'.encode())
        # case where the user isn't in that room
        elif sender_name not in self.rooms[room_to_leave].clients.keys():
            sender_socket.send(f'Error: You are not in {room_to_leave}\n'.encode())
        # otherwise leave
        else:
            self.rooms[room_to_leave].remove_client_from_room(sender_name, sender_socket)
            # remove the room if it's empty.
            if len(self.rooms[room_to_leave].clients) == 0:
                # make sure we don't accidentally delete the default room!
                if room_to_leave != DEFAULT_ROOM_NAME:
                    del self.rooms[room_to_leave]
            # send user back to #lobby
            self.rooms[DEFAULT_ROOM_NAME].add_client_to_room(sender_name, sender_socket)

    # Check if rooms exist, check if user is in room,
    # if room exists and user is in it then send message, otherwise skip
    def message_rooms(self, rooms_to_send, sender_name, message, sender_socket):
        '''
        send a message to a chatroom or list of chatrooms (assuming they exist)

        parameters
        ------------
        - rooms_to_send = list[str] of '#room_name' or single room name (str)
        - sender_socket = sender socket() instance.
        - sender_name = string
        - message = string
        '''
        # case where we want to send to a single room
        if type(rooms_to_send) == str:
            if rooms_to_send not in self.rooms.keys():
                sender_socket.send(f'Error: {rooms_to_send} does not exist!'.encode())
            if sender_socket not in self.rooms[rooms_to_send].client_sockets:
                sender_socket.send(f'Error: You are not in {rooms_to_send}!'.encode())
            else:
                message_broadcast(self.rooms[rooms_to_send], sender_name, message, sender_socket)

        # case where we want to message a series of rooms
        elif type(rooms_to_send) == list:
            for room in rooms_to_send:
                if room not in self.rooms:
                    sender_socket.send(f'Error: {room} does not exist'.encode())
                    continue
                if sender_socket not in self.rooms[room].client_sockets:
                    sender_socket.send(f'Error: You are not in {room}'.encode())
                    continue
                message_broadcast(self.rooms[room], sender_name, message, sender_socket)
    
    # block a user
    def block(self, user_name, to_block):
        '''
        blocks a user from DM'ing someone. this is a wrapper for User()
        '''
        for u in self.users:
            if u == user_name:
                user = self.users[user_name]
                user.block(to_block)

    # unblock a user
    def unblock(self, user_name, to_unblock):
        '''
        unblocks a user. this is a wrapper for User()
        '''
        for u in self.users:
            if u == user_name:
                user = self.users[user_name]
                user.unblock(to_unblock)

    # main message parser.
    def message_parser(self, message, sender_name, sender_socket):
        '''
        top-level entry point for messages to the application. 

        parameters 
        -----------
        - message = ''
        - sender_name = ''
        - sender_socket = sender socket() object

        message strings are split into word lists, then parsed accordingly.

        messages should, by default, go out the room the user is currently in.
        no need for a #room_name specification. 

        #lobby is the default room that any user can be in at any given time, 
        and is the one new users are sent to by default.

        commands
        ----------
        - /join #room_name
            - join a chatroom. a new one will be created if it doesn't already exist.

        - /leave #room_name
            - leave current room. if you are in the main lobby, you will be asked if you 
              want to exit. if yes, then client will terminate.

        - /list (opt) #room_name. 
            - will list all members active in the application by default. 
            - you can also specifiy n number of rooms to get user lists, assuming those rooms exist. 
            - if not, it will be skipped and the user will be notified of its non-existance.

        - /message <user>
            - send a direct message to another user, regardless if they're in the same room with you.

        - /block <user>
            - block DM's from other users

        - /unblock <user>
            - unblocks a user

        - /help
            - displays a list of available commands

        - /quit
            - leave current instance.

        NOTE: /quit and /help are handled on the client side!

        NOTE: Will need to coordinate with the CLI instance on the Client application!
        '''
        
        '''TEST OUTPUT'''
        if self.debug:
            print(f"\napp.message_parser() \nsender sock: {sender_socket} \nsender_name: {sender_name} \nmessage: {message}")
            print(f'message as word list: {message.split()}')

        # send message to room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            # find the room, then send message
            room = self.get_current_room(sender_name)
            if self.debug:
                print(f'Sender: {sender_name} \nRoom: {room} \nMessage: {message}\n')
            message_broadcast(self.rooms[room], sender_name, sender_socket, message)

        # Case where user wants to join a room:
        elif message.split()[0] == "/join":
            if len(message.strip().split()) < 2:
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode('ascii'))
            else:
                self.join_room(message.split()[1], sender_name, sender_socket)

        # Case where user wants to leave a room:
        elif message.split()[0] == "/leave":
            if len(message.strip().split()) < 2:
                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))
            else:
                room_to_leave = message.strip().split()[1]
                if room_to_leave[0] != "#":
                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode('ascii'))
                else:
                    # leave room...
                    sender_socket.send(f'Leaving {room_to_leave}...'.encode('ascii'))
                    self.leave_room(room_to_leave, sender_name, sender_socket)
                    # ... then send back to #lobby
                    sender_socket.send(f'Rejoining {DEFAULT_ROOM_NAME}...\n'.encode('ascii'))
                    self.join_room(DEFAULT_ROOM_NAME, sender_name, sender_socket)


        # Case where user wants to list all (or some) active members in the app
        '''NOTE: must check for multiple room names! If more than one, compile into single list'''
        # elif message.split()[0] == "/list"


        # Case where user wants to directly message another user
        '''NOTE: must check for username after /message too!'''    
        # elif message.split()[0] == "/message":


        # Case where user wants to block DM's from another user
        # elif message.split()[0] == "/block":


        # Case where user wants to un-block another user.
        # elif message.split()[] == "/unblock":



#------------------------------------------------------------------------------------------------------------------------------#

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
        
        message = f"{client_name} has joined the room!\n"
        message_broadcast(self, client_name, new_socket, message)

    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_room(self, client_name, client_socket):
        print(f'\nremoving {client_name} from {self.name}')

        self.clients.pop(client_name)

        message = f"{client_name} has left the room!\n"
        message_broadcast(self, client_name, client_socket, message)

    # returns a list of current users in this room as a string.
    def list_clients_in_room(self):
        return str([key for key in self.clients])


class User:

    def __init__(self, name, socket):
        self.name = name        # username
        self.socket = socket    # user's socket() object
        self.blocked = []       # list of blocked users (list[str])
        self.dms = {}           # dictionary of direct messages. key is sender, value is the message
    
    def get_dm(self, sender, message):
        '''
        ability to recieve DM's from another user.
        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key
        '''
        if sender not in self.blocked:
            self.dms[sender] = message
        else:
            print(f'{sender} is blocked!')
    
    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users. 
        '''
        dms = []
        if len(self.dms) > 0:
            for sender in self.dms:
                print(f'{sender} : {self.dms[sender]}\n')
                dms.append(f'{sender} : {self.dms[sender]}\n')
        return dms

    def read_dm(self, sender):
        '''
        displays a message from a single user
        '''
        if len(self.dms) > 0:
            if sender in self.dms.keys():
                print(f'From: {sender}: \n{self.dms[sender]}\n')
            else:
                print(f'No messages from {sender}!\n')

    def block(self, sender):
        '''
        block another user
        '''
        if sender not in self.blocked:
            self.blocked.append(sender)
    
    def unblock(self, sender):
        '''
        unblock another user.
        '''
        if sender in self.blocked:
            self.blocked.pop(sender)
