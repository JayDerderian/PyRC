'''
Jay Derderian
CS 594

Application module - the core functionality of the IRC Chat program.

This handles tracking of clients and their associated sockets, sending
and recieving messages, message parsing, and other neccessary functionality.
'''

import logging

from app.user import User
from app.chatroom import Chatroom

DEBUG = True
if DEBUG:
    logging.basicConfig(filename='IRC_App.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_ROOM_NAME = '#lobby'

# Broadcast a message to all clients in a given room
def message_broadcast(room, sender_name, message, debug=False):
    '''
    sends a message to all the users in a Chatroom() instance

    parameters
    -----------
    - room = Chatroom() object
    - sender_name = senders name (str)
    - message = message string
    - debug (optional) 
    '''
    if debug:
        print(f'\nirc.message_broadcast() \nSending message from {sender_name} to room {room.name}: \nMessage: {message}')
        logging.info(f'irc.message_broadcast() \nSending message from {sender_name} to room {room.name}: \nMessage: {message}')
    # Send the message to all clients in this room *except* the one that sent the messaage
    for client in room.clients:
        room.clients[client].send(f'{room.name} {sender_name} : {message}'.encode('ascii'))


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

        # Dictionary of active rooms. 
        # Key is room name (str), value is the Chatroom() object. 
        # #lobby room is always present by default, even if its empty.
        self.rooms = {}
        self.rooms[DEFAULT_ROOM_NAME] = Chatroom(room_name= DEFAULT_ROOM_NAME) 

        # Dictionary of active users
        # Key is username, value is User() object
        self.users = {}

    # add a new user to the instance
    def add_user(self, user_name, new_user_socket):
        if user_name not in self.users.keys():
            self.users[user_name] = User(name=user_name, 
                                         socket=new_user_socket)
            # add them to default lobby.
            self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(user_name, new_user_socket)
            if self.debug:
                logging.info(f'app.add_user() \nadding {user_name} and creating User() object: \n{type(self.users[user_name])}')
        else:
            if self.debug:
                logging.info(f'app.add_user() {user_name} is already in the server!')
            print(f'{user_name} is already in the server!')

    # remove a user from the instance
    def remove_user(self, user_name):
        if user_name in self.users.keys():
            del self.users[user_name]
        else:
            print(f'\napp.remove)user \n{user_name} is not in the server!')
    
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
        returns the room name (str) a user is currently in.
        '''
        room = ''
        if self.debug:
            print(f'\napp.get_current_room() - trying to find room {user_name} is currently in...')
            logging.info(f'app.get_current_room() \ntrying to find room {user_name} is currently in...')
        for r in self.rooms:
            if self.rooms[r].has_user(user_name):
                room = r
        if room == '':
            raise ValueError(f"{user_name} is not in a room!")
        return room

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
        if self.debug:
            print(f'\napp.join_room() \nattempting to add {sender_name} to {room_to_join}...')
            logging.info(f'app.join_room() \nattempting to add {sender_name} to {room_to_join}...')
        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            self.create_room(room_to_join, sender_name, sender_socket)
        # Case where it DOES already exist
        else:
            message = self.rooms[room_to_join].add_client_to_room(sender_name, sender_socket)
            message_broadcast(self.rooms[room_to_join], sender_name, message, self.debug)

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
        message = self.rooms[room_to_join].add_new_client_to_room(sender_name, sender_socket)
        if self.debug:
            print(f'\napp.create_room() \ncreating new Chatroom() instance: \n{self.rooms[room_to_join]}')
            print(f'\napp.create_room() \ncurrent members: {str(self.rooms[room_to_join].list_users_in_room())}')
            logging.info(f'app.create_room() \ncreating new Chatroom() instance: \n{self.rooms[room_to_join]}')
            logging.info(f'app.create_room() \ncurrent members: {str(self.rooms[room_to_join].list_users_in_room())}')
        message_broadcast(self.rooms[room_to_join], sender_name, message, self.debug)

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
            sender_socket.send(f'Error: {room_to_leave} does not exist\n'.encode('ascii'))

        # case where the user isn't in that room
        elif sender_name not in self.rooms[room_to_leave].clients.keys():
            sender_socket.send(f'Error: You are not in {room_to_leave}\n'.encode('ascii'))

        # otherwise leave
        else:
            if self.debug:
                print(f"\napp.leave_room() - Removing {sender_name} from {room_to_leave}...")
                logging.info(f'app.leave_room() \nRemoving {sender_name} from {room_to_leave}...')

            exit_message = self.rooms[room_to_leave].remove_client_from_room(sender_name)
            
            if self.debug:
                print(f'\napp.leave_room() - sending exit message: {exit_message} \nto sender_socket: {sender_socket}')
                logging.info(f'app.leave_room() \nsending exit message: {exit_message} \nto sender_socket: {sender_socket}')
            
            # make sure we don't broadcast to an empty room...
            if len(self.rooms[room_to_leave].clients) > 0:
                message_broadcast(self.rooms[room_to_leave], sender_name, exit_message, self.debug)

            # remove the room if its empty.
            if len(self.rooms[room_to_leave].clients) == 0:
                # make sure we don't accidentally delete the default room!
                if room_to_leave != DEFAULT_ROOM_NAME:
                    del self.rooms[room_to_leave]

            # send user back to #lobby
            join_message = self.rooms[DEFAULT_ROOM_NAME].add_client_to_room(sender_name, sender_socket)

            if self.debug:
                print(f'\napp.leave_room() - sending join message: {join_message} \nto sender_socket: {sender_socket}')
                logging.info(f'app.leave_room() \nsending join message: {join_message} \nto sender_socket: {sender_socket}')

            message_broadcast(self.rooms[DEFAULT_ROOM_NAME], sender_name, join_message, self.debug)

    # directly message another user
    def send_dm(self, sender, message, receiver):
        '''
        directly message another user. 
        wont send message if sender has been blocked by receiver!

        this works with the User() object.

        parameters
        ------------
        - sender = '' (name of sender)
        - message = ''
        - reciever = '' (name of sender)
        '''
        # find receiver
        for u in self.users:
            if u == receiver:
                user = self.users[receiver]
                break
        # find sender socket to send return message
        for s in self.users:
            if s == sender:
                sender_ = self.users[sender]
        # make sure sender isn't blocked by receiver
        if user.has_blocked(sender):
            sender_.socket.send(f'You were blocked by {receiver}!'.encode('ascii'))
            print(f'{sender} has been blocked by {receiver}!')
        else:
            # save message to User() instance. 
            # User() will send message via the user's socket.
            user.get_dm(sender, message)

    def get_dm(self, receiver, sender=None):
        '''
        gets a user's direct messages. works with the User() object.
        this also sends the 

        parameters
        ------------
        receiver = '' (user requesting dms)
        sender = None (set to user_name string if user wants 
                       dms from a specific user)
        '''
        # find receiver
        for u in self.users:
            if u == receiver:
                user = self.users[receiver]
                break
        if sender is None:
            return user.read_all_dms()
        else:
            return user.read_dms(sender)
    
    # block a user
    def block(self, user_name, to_block):
        '''
        blocks a user from DM'ing someone. 
        this is a wrapper for User().block(user_name)
        '''
        for u in self.users:
            if u == user_name:
                self.users[u].block(to_block)
                break

    # unblock a user
    def unblock(self, user_name, to_unblock):
        '''
        unblocks a user. 
        this is a wrapper for User().unblock(user_name)
        '''
        for u in self.users:
            if u == user_name:
                self.users[u].unblock(to_unblock)
                break

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

        - /users (opt) #room_name. 
            - will list *all members* active in the application by default. 
            - you can also specifiy n number of rooms to get user lists, assuming those rooms exist. 
            - if not, it will be skipped and the user will be notified of its non-existance.

        - /message <user>
            - send a direct message to another user, regardless if they're in the same room with you.
        
        - /dms (opt) <from_user>
            - gets *all* your direct messages and who they're from by default.
            - specify <from_user> if you want to see messages from a specific person.

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
        
        if self.debug:
            print(f"\napp.message_parser() \nsender_name: {sender_name} \nmessage: {message}")
            print(f'message as word list: {message.split()}')
            logging.info(f"app.message_parser() \nsender sock: {sender_socket} \nsender_name: {sender_name} \nmessage: {message} \nmessage as word list: {message.split()}")

        # send message to room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            # find the room, then send message
            room = self.get_current_room(sender_name)
            if self.debug:
                print(f'\napp.message_parser() "/" check \nsender: {sender_name} \nroom: {room} \nmessage: {message}\n')
                logging.info(f'app.message_parser() \nSender: {sender_name} \nRoom: {room} \nMessage: {message}\n')
            message_broadcast(self.rooms[room], sender_name, message, self.debug)

        # Case where user wants to join a room:
        elif message.split()[0] == "/join":
            if self.debug:
                print(f'\napp.message_parser() "/join case"')
            if len(message.strip().split()) < 2:
                if self.debug:
                    print(f'\napp.message_parser() \nSending /join error message to socket: \n {sender_socket}')
                    logging.info(f'app.message_parser() \nSending /join error message to socket: \n {sender_socket}')
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode('ascii'))
            else:
                self.join_room(message.split()[1], sender_name, sender_socket)

        # Case where user wants to leave a room:
        elif message.split()[0] == "/leave":
            if self.debug:
                print(f'\napp.message_parser() "/leave case"')

            # Case where user just submits "/leave"
            if len(message.strip().split()) < 2:
                if self.debug:
                    print(f'\napp.message_parser() \nSending /leave error message to socket: \n {sender_socket}')
                    logging.info(f'app.message_parser() \nSending /leave error message to socket: \n {sender_socket}')

                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))

            # otherwise try to remove...
            else:
                room_to_leave = message.strip().split()[1]
                if room_to_leave[0] != "#":
                    if self.debug:
                        print(f'\napp.message_parser() \nSending /leave #-syntax error message to socket: \n {sender_socket}')
                        logging.info(f'app.message_parser() \nSending /leave #-syntax error message to socket: \n {sender_socket}')

                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode('ascii'))
                else:
                    # leave room...
                    sender_socket.send(f'Leaving {room_to_leave}...'.encode('ascii'))

                    if self.debug:
                        print(f'\napp.message_parser() \nAttempting to remove {sender_name} from room {room_to_leave}...')
                        logging.info(f'app.message_parser() \nAttempting to remove {sender_name} from room {room_to_leave}...')

                    self.leave_room(room_to_leave, sender_name, sender_socket)

                    # ... then send back to #lobby
                    if self.debug:
                        print(f'\napp.message_parser() \nAttempting to send {sender_name} back to {DEFAULT_ROOM_NAME}...')
                        logging.info(f'app.message_parser() \nAttempting to send {sender_name} back to {DEFAULT_ROOM_NAME}...')

                    sender_socket.send(f'Rejoining {DEFAULT_ROOM_NAME}...\n'.encode('ascii'))
                    self.join_room(DEFAULT_ROOM_NAME, sender_name, sender_socket)

        # Case where user wants to list all (or some) active members in the app
        # NOTE: must check for multiple room names! If more than one, compile into single list
        elif message.split()[0] == "/users":
            # case where we want users from specific rooms
            if len(message.split()) > 1:
                # get any room names from the command
                message_ = message.split()
                rooms_to_list = []
                for word in message_:
                    if word[0] == '#':
                        rooms_to_list.append(word)
                # get users from each room
                user_list = []
                for room in self.rooms.keys():
                    # add room name up front before getting users
                    user_list.append(f'\n{room} users:\n')
                    user_list.extend(self.rooms[room].list_users_in_room())
                user_list = " \n".join(user_list)
                # send list back to client
                sender_socket.send(user_list.encode('ascii'))

            # case where we want *all* active members in the instance
            else:
                user_list = self.get_all_users()
                user_list = " \n".join(user_list)
                sender_socket.send(user_list.encode('ascii'))

        # Case where user wants to directly message another user
        # NOTE: must check for username after /message too!'''    
        elif message.split()[0] == "/message":
            # case where client doesn't include a user_name
            if len(message.split()) == 1:
                sender_socket.send('Error: must include a username. /message <user_name>'.encode('ascii'))
            # case where user tries to message more than one person at a time
            elif len(message.split()) > 2:
                sender_socket.send('Error:  can only DM one user at a time!'.encode('ascii'))
            # otherwise send message (blocked users are handled elsewhere!)
            else:
                receiver = message.split()[1]
                self.send_dm(sender_name, message, receiver)

        # Case where a user wants to check their direct messages
        elif message.split()[0] == "/dms":
            # check if there's a specific user they're looking for
            if len(message.split()) > 1:
                users = []
                message_ = message.split()
                for word in message_:
                    # skip the dm command
                    if word[0] == '/':
                        continue
                    users.append(word)
                # send each DM from each user
                for u in users:
                    self.get_dm(sender_name, sender=users[u])    

            # otherwise send all the dms
            self.get_dm(sender_name)
        
        # Case where user wants to block DM's from another user
        elif message.split()[0] == "/block":
            # case where the users messes up, yet again
            if len(message.split()) == 1:
                sender_socket.send('Error: /block requires at least one user_name argument!'.encode('ascii'))
            message_ = message.split()
            # remove the command, then iterate through list
            message_.pop(0)
            to_block = []
            for name in message:
                to_block.append(name)
            # send to User() to block each name sent in
            for name in to_block:
                self.block(sender_name, name)

        # Case where user wants to un-block another user.
        elif message.split()[0] == "/unblock":
            # case where the users messes up, yet again
            if len(message.split()) == 1:
                sender_socket.send('Error: /unblock requires at least one user_name argument!'.encode('ascii'))
            message_ = message.split()
            # remove the command, then iterate through list
            message_.pop(0)
            to_unblock = []
            for name in message:
                to_unblock.append(name)
            # send to User() to block each name sent in
            for name in to_unblock:
                self.unblock(sender_name, name)
