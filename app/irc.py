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
        logging.info(f'irc.message_broadcast() \nSending message from {sender_name} to room {room.name}: \nMessage: {message}\n')
    # Send the message to all clients in this room, including the sender.
    for client in room.clients:
        room.clients[client].send(f'{room.name} {sender_name} : {message}'.encode('ascii'))


# The container that has rooms, which have lists of clients
class IRC_App:
    '''
    The main IRC application. One default room - #lobby - is created when
    this class is instantiated. IRC_App() also keeps tracks of current users 
    and their socket info.

    IRC_App().message_parser(message:str) is the main point of entry for this
    application. All message strings recieved from the client should be sent 
    through here.

    Initialize IRC_App(debug=True) to create a logger and terminal read outs
    '''
    def __init__(self, debug=False):
        # Debuggin' stuff
        self.debug = debug
        if self.debug:
            logging.basicConfig(filename='IRC_App.log', 
                    filemode='w', 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')

        # Dictionary of active rooms. 
        # Key is room name (str), value is the Chatroom() object. 
        # #lobby room is always present by default, even if its empty.
        '''NOTE: Each Chatroom also has a dict of users and their objects!'''
        self.rooms = {}
        self.rooms[DEFAULT_ROOM_NAME] = Chatroom(room_name = DEFAULT_ROOM_NAME, 
                                                 debug = self.debug) 
        # Dictionary of active users
        # Key is username (str), value is User() object
        # Users can only be in one room at a time!
        self.users = {}

    # add a new user to the instance
    def add_user(self, user_name, new_user_socket):
        '''
        add a new user to app instance

        parameters
        ------------
        - user_name = ''
        - new_user_socket = socket() object
        '''
        # is this actually a new user?
        if user_name not in self.users.keys():
            # create new User() instance
            self.users[user_name] = User(name = user_name, 
                                         socket = new_user_socket,
                                         curr_room = DEFAULT_ROOM_NAME,
                                         debug = self.debug)
            # add them to default lobby.
            '''NOTE: do we need to update self.users[user].curr_name here too? 
                     does python make a copy of the object (pass by value) when passing
                     objects as arguments? not sure if self.users[user_name] and
                     chatroom.clients[user_name] will have the same value for curr_room...'''
            self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(self.users[user_name])
            if self.debug:
                logging.info(f'app.add_user() \nadding {user_name} and creating User() object: \n{self.users[user_name]}\n')

        # case where they're already in the instance
        else:
            if self.debug:
                logging.info(f'app.add_user() {user_name} is already in the server!\n')
            new_user_socket.send(f'{user_name} is already in this instance!'.encode('ascii'))

    # remove a user from the instance
    def remove_user(self, user_name):
        '''
        remove a user from app instance

        parameters
        -----------
        - user_name = ''
        '''
        if user_name in self.users.keys():
            del self.users[user_name]
        else:
            print(f'\napp.remove)user \n{user_name} is not in the server!')
    
    # get a list of active users in a specific room
    def get_users(self, room, sender_socket):
        if room in self.rooms.keys():
            users = self.rooms[room].get_users()
            sender_socket.send(str(users).encode('ascii'))
        else:
            sender_socket.send(f'{room} does not exist!'.encode('ascii'))

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
            logging.info(f'app.join_room() \nattempting to add {sender_name} to {room_to_join}...\n')

        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            # first remove user from their current room
            '''NOTE: double check against self.leave().
            maybe just use chatroom.remove_user_from_room()? don't want to send user
            back to lobby if they're trying to join a newly created room.'''
            room = self.users[sender_name].curr_room
            leave_message = self.rooms[room].remove_client_from_room(sender_name)
            # make sure we don't broadcast to an empty room...
            if len(self.rooms[room].clients) > 0:
                message_broadcast(self.rooms[room], sender_name, leave_message, self.debug)
            # then create new room.
            self.create_room(room_to_join, sender_name)

        # Case where it DOES already exist
        else:
            # Case where the user is already there
            if sender_name in self.rooms[room_to_join].clients.keys():
                sender_socket.send('You are already in this room, silly!'.encode('ascii'))
            # Leave current room, join new room
            else:
                # remove them from their current room
                '''NOTE: see note in app.add_user()!'''
                cur_room = self.users[sender_name].curr_room
                leave_message = self.rooms[cur_room].remove_user_from_room(sender_name)
                # make sure we don't broadcast to an empty room...
                if len(self.rooms[cur_room].clients) > 0:
                    message_broadcast(self.rooms[cur_room], sender_name, leave_message, self.debug)

                # add to room
                join_message = self.rooms[room_to_join].add_client_to_room(self.users[sender_name])
                message_broadcast(self.rooms[room_to_join], sender_name, join_message, self.debug)


    # Create a new Chatroom, add the room to the room list, and add the client to the chatroom
    # A room cannot exist without a client, so one must be supplied
    def create_room(self, room_to_join, sender_name):
        '''
        creates a new Chatroom() instance. 
        dont use directly! should only be called by self.join_room()

        parameters
        -------------
        - room_to_join = '#room_name
        - sender_name = ''
        - sender_socket = sender socket() object
        '''
        # create room, add user, and update their info
        self.rooms[room_to_join] = Chatroom(room_name = room_to_join, 
                                            debug = self.debug)
        '''NOTE: see note in app.add_user()!'''
        join_message = self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name]) 

        if self.debug:
            print(f'\napp.create_room() \ncreating new Chatroom() instance: \n{self.rooms[room_to_join]}')
            print(f'\napp.create_room() \ncurrent members: {str(self.rooms[room_to_join].list_users_in_room())}')
            logging.info(f'app.create_room() \ncreating new Chatroom() instance: \n{self.rooms[room_to_join]}\n')
            logging.info(f'app.create_room() \ncurrent members: {str(self.rooms[room_to_join].list_users_in_room())}\n')

        # send join message
        message_broadcast(self.rooms[room_to_join], sender_name, join_message, self.debug)

    # Check if the room exists, check if user is in the room,
    # remove user from room and delete room if it is empty
    def leave_room(self, room_to_leave, sender_name, sender_socket):
        '''
        leave a Chatroom() instance. will remove room if it's empty.
        sends user back to #lobby.

        parameters
        -------------
        - room_to_leave = '' (key for app.rooms dict)
        - sender_name = ''
        - sender_socket = sender socket() objet
        '''
        # case where room doesn't exist
        if room_to_leave not in self.rooms.keys():
            if self.debug:
                print(f"\napp.leave_room() -{room_to_leave} doesn't exist!")
                logging.error(f'app.leave_room() \nRoom {room_to_leave} doesnt exist!\n')            
            sender_socket.send(f'Error: {room_to_leave} does not exist\n'.encode('ascii'))


        # case where the user isn't in that room
        elif sender_name not in self.rooms[room_to_leave].clients.keys():
            if self.debug:
                print(f"\napp.leave_room() -{sender_name} isnt in that room!")
                logging.info(f'app.leave_room() \nUser {sender_name} isnt in that room!\n')   
            sender_socket.send(f'Error: You are not in {room_to_leave}\n'.encode('ascii'))

        # otherwise leave
        else:
            if self.debug:
                print(f"\napp.leave_room() - Removing {sender_name} from {room_to_leave}...")
                logging.info(f'app.leave_room() \nRemoving {sender_name} from {room_to_leave}...\n')

            # remove user from room
            '''NOTE: see note in app.add_user()!'''
            exit_message = self.rooms[room_to_leave].remove_client_from_room(sender_name)
            if self.debug:
                print(f'\napp.leave_room() - sending exit message: {exit_message} \nto sender_socket: {sender_socket}')
                logging.info(f'app.leave_room() \nsending exit message: {exit_message} \nto sender_socket: {sender_socket}\n')
            
            # make sure we don't broadcast to an empty room...
            if len(self.rooms[room_to_leave].clients) > 0:
                message_broadcast(self.rooms[room_to_leave], sender_name, exit_message, self.debug)

            # # remove the room if its empty.
            # if len(self.rooms[room_to_leave].clients) == 0:
            #     # make sure we don't accidentally delete the default room!
            #     if room_to_leave != DEFAULT_ROOM_NAME:
            #         del self.rooms[room_to_leave]

            # send user back to #lobby
            '''NOTE: see note in app.add_user()!'''
            join_message = self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(self.users[sender_name])
            if self.debug:
                print(f'\napp.leave_room() - sending join message: {join_message} \nto sender_socket: {sender_socket}')
                logging.info(f'app.leave_room() \nsending join message: {join_message} \nto sender_socket: {sender_socket}\n')

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
                receiver_ = self.users[receiver]
                break
        # find sender socket to send return message
        for s in self.users:
            if s == sender:
                sender_ = self.users[sender]
        # make sure sender isn't blocked by receiver
        if receiver_.has_blocked(sender):
            sender_.socket.send(f'You were blocked by {receiver}!'.encode('ascii'))
        else:
            # save message to User() instance. 
            # User() will send message via the user's socket.
            receiver_.get_dm(sender, message)

    def get_dm(self, receiver, sender=None):
        '''
        gets a user's direct messages. works with the User() object.
        this also sends the 

        parameters
        ------------
        - receiver = '' (user requesting dms)
        - sender = None (set to user_name string if user wants 
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

        - (No command) <message>
            - Send message to current room. #lobby is the default room.

        - /join #room_name
            - join a chatroom. a new one will be created if it doesn't already exist.

        - /leave #room_name
            - leave current room. if you are in the main lobby, you will be asked if you 
              want to exit. if yes, then client will terminate.

        - /message <user_name>
            - send a direct message to another user, regardless if they're in the same room with you.
            - these are asynchronous between users.
        
        - /dms (opt) <from_user>
            - gets *all* your direct messages and who they're from by default.
            - specify <from_user> if you want to see messages from a specific person.

        - /whisper <user_name>
            - directly message another user in real-time if they are in the same
              chatroom as you. these messages won't be seen by other users in the 
              room.

        - /block <user_name>
            - block DM's from other users

        - /unblock <user_name>
            - unblocks a user

        - /help
            - displays a list of available commands

        - /quit
            - leave current instance.

        TODO: add /whisper option for direct, real-time messages between two users! 
              either create a single room for two users or connect two User() instances.
              both will contain user socket objects.

        NOTE: /quit and /help are handled on the client side!

        NOTE: Will need to coordinate with the CLI instance on the Client application!
        '''
        
        if self.debug:
            print(f"\napp.message_parser() \nsender_name: {sender_name} \nmessage: {message}")
            print(f'message as word list: {message.split()}')
            logging.info(f"app.message_parser() \nsender sock: {sender_socket} \nsender_name: {sender_name} \nmessage: {message} \nmessage as word list: {message.split()}\n")

        # send message to room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            # find the room, then send message
            room = self.users[sender_name].curr_room
            if self.debug:
                print(f'\napp.message_parser() "/" check \nsender: {sender_name} \nroom: {room} \nmessage: {message}\n')
                logging.info(f'app.message_parser() \nSender: {sender_name} \nRoom: {room} \nMessage: {message}\n')
            message_broadcast(self.rooms[room], sender_name, message, self.debug)

        # Case where user wants to join a room:
        elif message.split()[0] == "/join":
            # Case where user just enters '/join'

            # Case where there's a typo or user forgot to add a room argument
            if len(message.strip().split()) < 2:
                if self.debug:
                    print(f'\napp.message_parser() /join \nSending /join error message to socket: \n {sender_socket}')
                    logging.info(f'app.message_parser() /join \nSending /join error message to socket: \n {sender_socket}\n')
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode('ascii'))

            # Case where the user is already in the room
            
            # Otherwise join or create the room.
            else:
                self.join_room(message.split()[1], sender_name, sender_socket)

        # Case where user wants to leave a room:
        elif message.split()[0] == "/leave":
            if self.debug:
                print(f'\napp.message_parser() "/leave case"')

            # Case where user just submits "/leave"
            if len(message.split()) == 1:
                if self.debug:
                    print(f'\napp.message_parser() /leave \nSending /leave error message to socket: \n {sender_socket}')
                    logging.info(f'app.message_parser() /leave \nSending /leave error message to socket: \n {sender_socket}\n')
                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))

            # otherwise try to remove...
            else:
                room_to_leave = message.strip().split()[1]
                # case where user forgets to include "#" in "#room_name"
                if room_to_leave[0] != "#":
                    if self.debug:
                        print(f'\napp.message_parser() /leave \nSending /leave #-syntax error message to socket: \n {sender_socket}')
                        logging.info(f'app.message_parser() /leave \nSending /leave #-syntax error message to socket: \n {sender_socket}\n')
                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode('ascii'))
                # leave room...
                else:
                    if self.debug:
                        print(f'\napp.message_parser() /leave \nAttempting to remove {sender_name} from room {room_to_leave}...')
                        logging.info(f'app.message_parser() /leave \nAttempting to remove {sender_name} from room {room_to_leave}...\n')
                    sender_socket.send(f'Leaving {room_to_leave}...'.encode('ascii'))
                    # this sends the user back to the #lobby!
                    self.leave_room(room_to_leave, sender_name, sender_socket)

        # # Case where user wants to directly message another user
        # # NOTE: must check for username after /message too!'''    
        # elif message.split()[0] == "/message":
        #     # case where client doesn't include a user_name
        #     if len(message.split()) == 1:
        #         sender_socket.send('Error: must include a username. /message <user_name>'.encode('ascii'))
        #     # case where user tries to message more than one person at a time
        #     elif len(message.split()) > 2:
        #         sender_socket.send('Error:  can only DM one user at a time!'.encode('ascii'))
        #     # otherwise send message (blocked users are handled elsewhere!)
        #     else:
        #         receiver = message.split()[1]
        #         self.send_dm(sender_name, message, receiver)

        # # Case where a user wants to check their direct messages
        # elif message.split()[0] == "/dms":
        #     # check if there's a specific user they're looking for
        #     if len(message.split()) > 1:
        #         users = []
        #         message_ = message.split()
        #         for word in message_:
        #             # skip the dm command
        #             if word[0] == '/':
        #                 continue
        #             users.append(word)
        #         # send each DM from each user
        #         for u in users:
        #             self.get_dm(sender_name, sender=users[u])    

        #     # otherwise send all the dms
        #     self.get_dm(sender_name)
        
        # # Case where user wants to block DM's from another user
        # elif message.split()[0] == "/block":
        #     # case where the users messes up, yet again
        #     if len(message.split()) == 1:
        #         sender_socket.send('Error: /block requires at least one user_name argument!'.encode('ascii'))
        #     message_ = message.split()
        #     # remove the command, then iterate through list
        #     message_.pop(0)
        #     to_block = []
        #     for name in message:
        #         to_block.append(name)
        #     # send to User() to block each name sent in
        #     for name in to_block:
        #         self.block(sender_name, name)

        # # Case where user wants to un-block another user.
        # elif message.split()[0] == "/unblock":
        #     # case where the users messes up, yet again
        #     if len(message.split()) == 1:
        #         sender_socket.send('Error: /unblock requires at least one user_name argument!'.encode('ascii'))
        #     message_ = message.split()
        #     # remove the command, then iterate through list
        #     message_.pop(0)
        #     to_unblock = []
        #     for name in message:
        #         to_unblock.append(name)
        #     # send to User() to block each name sent in
        #     for name in to_unblock:
        #         self.unblock(sender_name, name)

        # TEMP response
        else:
            sender_socket.send(f'{message.split()[0]} is not a valid command!'.encode('ascii'))