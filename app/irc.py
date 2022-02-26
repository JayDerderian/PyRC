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
                                         curr_room = DEFAULT_ROOM_NAME,
                                         socket = new_user_socket,
                                         debug = self.debug)
            # add them to default lobby.
            self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(self.users[user_name])
            join_message = f'{user_name} joined {DEFAULT_ROOM_NAME}!'
            # send join message to room
            message_broadcast(self.rooms[DEFAULT_ROOM_NAME], user_name, join_message, self.debug)
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
            return f'{user_name} is not in the server!'
    
    # get a list of active users in a specific room
    def get_users(self, room, sender_socket):
        if room in self.rooms.keys():
            users = self.rooms[room].get_users()
            sender_socket.send(users.encode('ascii'))
            return users
        else:
            sender_socket.send(f'{room} does not exist!'.encode('ascii'))
            return f'{room} does not exist!'

    # get a list of all active users
    def get_all_users(self):
        '''
        returns a str of all active users in the instance.
        '''
        users = list(self.users.keys())
        return " ".join(users)

    # returns a list of active rooms
    def list_all_rooms(self):
        '''
        returns a str of all active rooms.
        '''
        user_list = list(self.rooms.keys())
        return " ".join(user_list)
    
    # Check if the room name begins with '#', check if user is already in the room,
    # create the room if it does not exist, then join the room the user specified
    def join_room(self, room_to_join, sender_name, sender_socket, mult_room=False):
        '''
        join or create a new Chatroom() instance

        parameters
        --------------
        - room_to_join = '#room_name'
        - sender_name = ''
        - sender_socket = sender socket() object
        - multi_room = boolean (set to False by default)
        '''
        if self.debug:
            logging.info(f'app.join_room() \nattempting to add {sender_name} to {room_to_join}...\n')

        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            if self.debug:
                logging.info(f'app.join_room() \ncreating {room_to_join}...\n')
            '''
            NOTE: set mult_room to True to NOT remove a user from their current room! 
                  adding the ability to be active in multiple rooms means the user would
                  only want to use /leave instead of having /join handle it for them. 
            '''
            # Only remove users if they only want to be in one room at a time!
            if mult_room == False:
                room = self.users[sender_name].curr_room
                '''NOTE: iterate through user.curr_rooms to match against
                         room we want to leave? 
                '''
                self.users[sender_name].curr_rooms.remove(room)
                if self.debug:
                    logging.info(f'app.join_room() \nattempting to remove {sender_name} from {room}...\n')

                self.rooms[room].remove_client_from_room(sender_name)
                leave_message = f'{sender_name} left {room}!'
                # make sure we don't broadcast to an empty room...
                if len(self.rooms[room].clients) > 0:
                    message_broadcast(self.rooms[room], sender_name, leave_message, self.debug)

            # create new room.
            if self.debug:
                logging.info(f'app.join_room() \nremoved {sender_name} from {room}, creating {room_to_join}...\n')
            self.create_room(room_to_join, sender_name)
            sender_socket.send(f'Joined {room_to_join}!'.encode('ascii'))
            return f'Joined {room_to_join}!'

        # Case where it DOES already exist
        else:
            if self.debug:
                logging.info(f'app.join_room() \n{sender_name} attempted to join pre-existing room {room_to_join}...\n')
                logging.info(f'{room_to_join} info: \ninstance: {self.rooms[room_to_join]} \nmembers: {self.rooms[room_to_join].get_users()}\n')
            # Case where the user is already there
            if self.rooms[room_to_join].has_user(sender_name):
                if self.debug:
                    logging.info(f'app.join_room() \n{sender_name} attempted to join a room they are in! room {room_to_join}\n')
                sender_socket.send('You are already in this room, silly!'.encode('ascii'))
            # Only remove users if they only want to be in one room at a time!
            if mult_room == False:
                # Leave current room, join new room
                # remove them from their current room
                cur_room = self.users[sender_name].curr_room
                self.users[sender_name].curr_rooms.remove(cur_room)
                if self.debug:
                    logging.info(f'app.join_room() \n{sender_name} is trying to move from room {cur_room}...')
                    logging.info(f'{sender_name} listed current room: {self.users[sender_name].curr_room}\n')
                    logging.info(f'{cur_room} info: \ninstance: {self.rooms[cur_room]} \nmembers: {self.rooms[cur_room].get_users()}\n')

                self.rooms[cur_room].remove_client_from_room(sender_name)
                leave_message = f'{sender_name} left {cur_room}!'
                if self.debug:
                    logging.info(f'app.join_room() \nremoved {sender_name} from {cur_room}!')

                # make sure we don't broadcast to an empty room...
                if len(self.rooms[cur_room].clients) > 0:
                    if self.debug:
                        logging.info(f'app.join_room() \nattempting to send leave message: {leave_message}')
                    message_broadcast(self.rooms[cur_room], sender_name, leave_message, self.debug)

            # add to room
            join_message = f'{sender_name} joined {room_to_join}!'
            self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name])
            if self.debug:
                logging.info(f'\napp.join_room() \n{sender_name} joined {room_to_join}!')
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
        '''
        # create room, add user, and update their info (handled in room.add_new_client_to_room())
        self.rooms[room_to_join] = Chatroom(room_name = room_to_join, debug = self.debug)
        self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name]) 
        if self.debug:
            logging.info(f'app.create_room() \ncreating new Chatroom() instance: \n{self.rooms[room_to_join]}\n')
            logging.info(f'app.create_room() \ncurrent members: {str(self.rooms[room_to_join].get_users())}\n')

        # send join message
        join_message = f'{sender_name} joined {room_to_join}!'
        if self.debug:
            logging.info(f'app.create_room() \nSending join message: {join_message}\n')
        message_broadcast(self.rooms[room_to_join], sender_name, join_message, self.debug)

    # Check if the room exists, check if user is in the room,
    # remove user from room and delete room if it is empty
    def leave_room(self, room_to_leave, sender_name, sender_socket, prev_room=False):
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
                logging.error(f'app.leave_room() \nRoom {room_to_leave} doesnt exist!\n')            
            sender_socket.send(f'Error: {room_to_leave} does not exist\n'.encode('ascii'))


        # case where the user isn't in that room
        elif self.rooms[room_to_leave].has_user(sender_name) == False:
            if self.debug:
                logging.info(f'app.leave_room() \nUser {sender_name} isnt in that room!\n')   
            sender_socket.send(f'Error: You are not in {room_to_leave}\n'.encode('ascii'))

        # otherwise leave
        else:
            if self.debug:
                logging.info(f'app.leave_room() \nRemoving {sender_name} from {room_to_leave}...\n')

            # remove user from room
            self.rooms[room_to_leave].remove_client_from_room(sender_name)
            exit_message = f'{sender_name} left {room_to_leave}!'
            if self.debug:
                logging.info(f'app.leave_room() \nsending exit message: {exit_message} \nto sender_socket: {sender_socket}\n')
            
            # make sure we don't broadcast to an empty room...
            if len(self.rooms[room_to_leave].clients) > 0:
                message_broadcast(self.rooms[room_to_leave], sender_name, exit_message, self.debug)
            '''
            NOTE: if multi-room abilities are being used, asked the user if they want to go back
                  to a previous room they've been to (check user.curr_rooms), or if they'd like 
                  to go back to the lobby
            '''
            # send user back to #lobby
            self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(self.users[sender_name])
            join_message = f'{sender_name} joined {DEFAULT_ROOM_NAME}!'
            if self.debug:
                logging.info(f'app.leave_room() \nsending join message: {join_message} \nto sender_socket: {sender_socket}\n')

            message_broadcast(self.rooms[DEFAULT_ROOM_NAME], sender_name, join_message, self.debug)
 
    # message another user privately in a shared room
    def send_whisper(self, sender_name, message, receiver):
        '''
        privately message another user in a shared chatroom.
        ideally the message will only be seen between the two users,
        even if there are other users in the room

        parameters
        ----------
        - sender = '' (sender of the whisper)
        - message = '' (note: full entereted text! command and username are still
                        part of this string)
        - receiver = '' (receiver of the whisper)
        '''

        if self.debug:
            logging.info(f'app.message_parser() /whisper \nsearching for {receiver}...\n')
        
        # case where receiver is not in app instance
        if receiver not in self.users.keys():
            if self.debug:
                logging.error(f'app.message_parser() /whisper \nERROR: {receiver} not in app instance!\n')                    
            self.users[sender_name].send(f'Error: {receiver} not in application instance!'.encod('ascii'))

        # case where receiver blocked sender
        elif self.users[receiver].has_blocked(sender_name):
            if self.debug:
                logging.info(f'app.message_parser() /whisper \nERROR: {receiver} blocked {sender_name}!')
            self.users[sender_name].send(f'Error: you were blocked by {receiver}!'.encode('ascii'))

        # otherwise, try to send whisper
        else:
            # make sure sender and receiver are in the same room
            if self.users[sender_name].curr_room == self.users[receiver].curr_room:
                # remove command and username arguments
                message_text = message.split()
                message_text = message_text[2:]
                message_text = f'/whisper @{sender_name}: {" ".join(message_text)}'
                if self.debug:
                    logging.info(f'app.message_parser() /whisper \{sender_name} sending message to {receiver} \nmessage: {message_text}\n')
                # send message to receiver
                self.users[receiver].send(message_text.encode('ascii'))

            else:
                if self.debug:
                    logging.info(f'app.message_parser() /whisper \n{sender_name} not in same room as {receiver}!\n')
                # send error message to sender
                self.users[sender_name].send(f'Error: you are not in the same room as {receiver}!'.encode('ascii'))

    # directly message another user
    def send_dm(self, sender, message, receiver):
        '''
        directly message another user. 

        parameters
        ------------
        - sender = '' 
        - message = ''
        - reciever = '' 

        wont send message if sender has been blocked by receiver!
        receiver gets a notification message that they've received
        a direct message from another user.
        '''
        # make sure receiver is in the instance
        if receiver not in self.users.keys():
            if self.debug:
                logging.info(f'app.send_dm() \nERROR: {receiver} not in app instance!\n')
            self.users[sender].send(f'Error: {receiver} not in app instance!'.encode('ascii'))
        else:
            # save message to User() instance. 
            # User() will send notification message to receiver.
            # User() will also check whether sender was blocked by receiver.
            if self.debug:
                logging.info(f'app.send_dm() \nsender: {receiver} \nmessage: {message}!\n')
            self.users[receiver].get_dm(sender, message)

    def read_dms(self, receiver, sender=None):
        '''
        gets a user's direct messages. works with the User() object.
        this also sends the 

        parameters
        ------------
        - receiver = '' (user requesting dms)
        - sender = None (set to user_name string if user wants 
                         dms from a specific user)
        '''
        if sender is None:
            return self.users[receiver].read_all_dms()
        else:
            return self.users[receiver].read_dm(sender)
    
    # block a user
    def block(self, user_name, to_block):
        '''
        blocks a user from DM'ing someone. 
        this is a wrapper for User().block(user_name)
        '''
        self.users[user_name].block(to_block)

    # unblock a user
    def unblock(self, user_name, to_unblock):
        '''
        unblocks a user. 
        this is a wrapper for User().unblock(user_name)
        '''
        self.users[user_name].unblock(to_unblock)
    
    # parse a username
    def parse_user_name(self, user_name):
        '''
        removes the @ symbol when a username is used as an argument, i.e. '@user_name'

        parameters
        -----------
        - user_name = ''
        '''
        name = [w for w in user_name]
        name.remove('@')
        return ''.join(name)

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
        and is where new users are sent to when they first join the app instance.

        commands
        ----------

        - (No command) <message>
            - Send message to current room. #lobby is the default room.

        - /rooms
            - list all currently active rooms in app instance

        - /join #room_name (opt) #room_name2 #room_name3 ...
            - join a chatroom. a new one will be created if it doesn't already exist.
            - to join multiple rooms, add additional room names separated by a space

        - /leave #room_name
            - leave current room. user will be sent back to #lobby by default 
            - if you are in the main lobby, you will be asked if you 
              want to exit. if yes, then client will terminate.
            - if user().curr_rooms[] > 1, you will be asked which room
            - you'd like to go back to, otherwise you'll go back to the #lobby.
        
        - /users
            - list all other users in the room the client is currently in

        - /broadcast #room_name1 <message_1> #room_name2 <message_2>...
            - broadcast *distinct* messages to *multiple* rooms

            - after command, user will be shown a list of active rooms
              and they can select which rooms they want to broad cast too, 
              and in what order.

            - message input will be prompted with each room they listed

        - /message @<user_name> <message>
            - send a direct message to another user, regardless if they're in the 
              same room with you.
            - these are asynchronous between users.
        
        - /dms (opt) <from_user>
            - gets *all* your direct messages and who they're from by default.
            - specify <from_user> if you want to see messages from a specific person.

        - /whisper @<user_name> <message>
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

        NOTE: /quit and /help are handled on the client side!

        NOTE: Will need to coordinate with the TUI instance on the Client application!
        '''
        if self.debug:
            logging.info(f"app.message_parser() \nsender sock: {sender_socket} \nsender_name: {sender_name} \nmessage: {message} \nmessage as word list: {message.split()}\n")

        # send message to room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            # find the room, then send message
            room = self.users[sender_name].curr_room
            if self.debug:
                logging.info(f'app.message_parser() \nSender: {sender_name} \nRoom: {room} \nMessage: {message}\n')
            message_broadcast(self.rooms[room], sender_name, message, self.debug)

        #### Case where user wants to join a room ###:
        elif message.split()[0] == "/join":
            '''
            syntax : /join #room_name1 (opt) #room_name2 etc...
            '''
            # case where there's a typo or user forgot to add a room argument
            if len(message.split()) < 2:
                if self.debug:
                    logging.error(f'app.message_parser() /join \nSending /join error message to socket: \n {sender_socket}\n')
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode('ascii'))
                return "/join requires a #room_name argument.\nPlease enter: /join #roomname\n"

            # case where first room arg doesn't have '#' symbol in front of it
            elif '#' not in message.split()[1]:
                if self.debug:
                    logging.error(f'app.message_parser() /join \nERROR: no "#" in room name argument!\n')
                sender_socket.send("/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n".encode('ascii'))
                return "/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n"

            # case where the user is already in the room
            # ****NOTE: move this down to the loop in the else-block below?****
            elif message.split()[1] == self.users[sender_name].curr_room:
                sender_socket.send(f'Error: you are already in {message.split()[1]}!')
                return f'Error: you are already in {message.split()[1]}!'
            
            # otherwise try to join or create room(s).
            else:
                
                # ******************************************
                # TODO: 
                #   Add ability to join multiple rooms!
                # ******************************************
                '''
                # check if there's more than one room argument

                # NOTE: this might take any words in the message that accidentally
                # start with # and treat it as a room name, potentially breaking
                # the while message apart. need a way to separate end of message
                # with a deliminator of sorts.
                
                if len(message.split()) > 2:
                    rooms_to_join = []
                    for word in message.split():
                        if word[0] == '#':
                            rooms_to_join.append(word)

                    # attempt to add user to these rooms
                    for room in rooms_to_join:
                        # make sure user isn't already in this room
                        if room not in self.users[sender_name].curr_rooms:
                            self.join_room(room, sender_name, sender_socket)
                            self.users[sender_name].curr_rooms.append(room)
                        else:
                            sender_socket.send(f'You are already in {room_to_join[room]}!'.encode('ascii))
                else:
                '''
                if self.debug:
                    logging.info(f'app.message_parser() /join \nattempting to join {message.split()[1]}...\n')
                # add conditon to check whether user is in this room here too...
                self.join_room(message.split()[1], sender_name, sender_socket)

        ### Case where user wants to leave a room ###:
        elif message.split()[0] == "/leave":

            # Case where user just submits "/leave"
            if len(message.split()) == 1:
                if self.debug:
                    logging.info(f'app.message_parser() /leave \nSending /leave error message to socket: \n {sender_socket}\n')
                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))

            # otherwise try to remove...
            else:
                room_to_leave = message.strip().split()[1]
                # case where user forgets to include "#" in "#room_name"
                if room_to_leave[0] != "#":
                    if self.debug:
                        logging.info(f'app.message_parser() /leave \nSending /leave #-syntax error message to socket: \n {sender_socket}\n')
                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode('ascii'))
                # leave room...
                else:
                    if self.debug:
                        logging.info(f'app.message_parser() /leave \nAttempting to remove {sender_name} from room {room_to_leave}...\n')
                    sender_socket.send(f'Leaving {room_to_leave}...'.encode('ascii'))
                    # this sends the user back to the #lobby!
                    self.leave_room(room_to_leave, sender_name, sender_socket)

        ### Case where user wants to list all active rooms ###:
        elif message.split()[0] == "/rooms":
            if len(self.rooms) > 0:
                rooms = f'Active rooms: \n{self.list_all_rooms()}'
                sender_socket.send(rooms.encode('ascii'))
            else:
                sender_socket.send('Error: no active rooms!'.encode('ascii'))

        ### Case where user wants list of other users in their current room ###
        elif message.split()[0] == "/users":
            # get users current room
            cur_room = self.users[sender_name].curr_room
            # make sure cur_room is accurate...
            if cur_room in self.rooms.keys():
                # get user list from room
                user_list = f'{cur_room} users: \n{self.rooms[cur_room].get_users()}'
                sender_socket.send(user_list.encode('ascii'))
            else:
                sender_socket.send(f'Error: unable to get users for room {cur_room}!'.encode('ascii'))

        ### Case where user wants to send *distinct* messages to *multiple* rooms ###
        # elif message.split()[0] == "/broadcast"

            # command syntax: /broadcast #room_name1 <message1> | #room_name2 <message2> |... etc.
            
            # remove /broadcast command 

            # loop:
            #   get room name, check if there's people in it
            #       if yes, send message
            #       else, skip 

            # only broadcast to rooms with people in them!

            # check to make sure '|' preceeds another #room_name to ensure we reached the end of the message


        ### Case where user wants to directly message another user ###
        elif message.split()[0] == "/message":
            '''
            syntax - /message @user_name <message>
            '''
            if self.debug:
                logging.info('app.message_parser() \n/message case\n')
            # case where client doesn't include a user_name
            if len(message.split()) == 1:
                if self.debug:
                    logging.info('app.message_parser() /message \nERROR: not enough @user_name args\n')
                sender_socket.send('Error: /message requires a username argument. \nex: /message @<user_name> <message>'.encode('ascii'))
                return 'Error: /message requires a username argument. \nex: /message @<user_name> <message>'
            # case where user tries to message more than one person at a time.
            # elif message.split().count('@') > 1:
            elif list(message).count('@') > 1:
                if self.debug:
                    logging.info('app.message_parser() \nERROR: too many @s!\n')
                sender_socket.send('Error: /message only takes one username argument. \nex: /message @<user_name> <message>'.encode('ascii'))
                return 'Error: /message only takes one username argument. \nex: /message @<user_name> <message>'
            # remove /message and @user_name, then send the remaining message
            else:
                if self.debug:
                    logging.info(f'app.message_parser() \nremoving /message and @user_name from: {message.split()}\n')
                message_ = message.split()
                # remove command
                message_.pop(0)
                # get receiver's name & remove @ symbol
                receiver = self.parse_user_name(message_[0])
                # remove username from message text
                message_.pop(0)
                message_text = ' '.join(message_)
                if self.debug:
                    logging.info(f'app.message_parser() /message \nreceiver {receiver} \nfinal message text: {message_text}\n')
                # send
                self.send_dm(sender_name, message_text, receiver)
                
        ### Case where a user wants to check their direct messages ###
        elif message.split()[0] == "/dms":
            '''
            syntax - /dms (opt) @<sender_name> 
            '''
            # check if there's a specific user they're looking for
            if len(message.split()) > 1:
                if self.debug:
                    logging.info('app.message_parser() /dms \n/dms case\n')
                dm_sender = message.split()[1]
                if dm_sender[0] == '@':
                    # remove @ symbol
                    dm_sender = self.parse_user_name(dm_sender)
                    # get dm's
                    if self.debug:
                        logging.info(f'app.message_parser() /dms \nsender: {dm_sender} sent to self.read_dms()\n')
                    self.read_dms(sender_name, dm_sender)
                else:
                    sender_socket.send('Error: /message requires a "@" character to denote a user, ie @user_name'.encode('ascii'))
                    return 'Error: /message requires a "@" character to denote a user, ie @user_name'
            # otherwise just get all their dms
            else:
                # otherwise retrieve all dms for this user
                self.read_dms(sender_name)

        ### Case where a user wants to whisper to another user in the same chatroom ###
        elif message.split()[0] == '/whisper':

            # check if user is in same room with username arg aver /whisper. if so, check if sender
            # is blocked by receiver of /whisper. if not, then send message with the syntax:
            # <whisper> <sender> : <message>

            # case where there's no username or text argument
            if len(message.split()) == 1:
                if self.debug:
                    logging.error('app.message_parser() /whisper \nERROR: No username argument found!')
                sender_socket.send('Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'.encode('ascii'))
                return 'Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'

            # case where we try to message more than one user
            if list(message).count('@') > 1: 
                if self.debug:
                    logging.error('app.message_parser() /whisper \nERROR: too many username arguments found!\n')
                sender_socket.send('Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'.encode('ascii'))
                return 'Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'

            # otherwise, get receiver name and send to method
            else:
                message_ = message.split()
                # remove command
                message_.pop(0)
                # get receiver's name & remove @ symbol
                receiver = message_[0]
                receiver = self.parse_user_name(receiver)
                self.send_whisper(sender_name, message, receiver)

        ### Case where user wants to block DM's from another user ###
        elif message.split()[0] == "/block":
            '''
            syntax: /block @user1 (opt) @user2...
            '''
            # case where the users messes up, yet again
            if len(message.split()) == 1:
                sender_socket.send('Error: /block requires at least one user_name argument!'.encode('ascii'))
                return 'Error: /block requires at least one user_name argument!'
            message_ = message.split()
            # remove the command, then iterate through list
            message_.pop(0)
            to_block = []
            for name in message_:
                # make sure we remove the '@' symbol. 
                if name[0] == '@':
                    to_block.append(self.parse_user_name(name))
            # send to User() to block each name sent in
            for name in to_block:
                self.block(sender_name, name)

        ### Case where user wants to un-block another user ###
        elif message.split()[0] == "/unblock":
            '''
            syntax: /unblock @user1 (opt) @user2...
            '''
            # case where the users messes up, yet again
            if len(message.split()) == 1:
                sender_socket.send('Error: /unblock requires at least one user_name argument!'.encode('ascii'))
                return 'Error: /unblock requires at least one user_name argument!'
            message_ = message.split()
            # remove the command, then iterate through list
            message_.pop(0)
            to_unblock = []
            for name in message_:
                if name[0] == '@':
                    to_unblock.append(self.parse_user_name(name))
            # send to User() to block each name sent in
            for name in to_unblock:
                self.unblock(sender_name, name)

        # anything else...
        else:
            sender_socket.send(f'{message.split()[0]} is not a valid command!'.encode('ascii'))
            return f'{message.split()[0]} is not a valid command!'