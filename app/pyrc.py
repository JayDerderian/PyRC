'''
Jay Derderian
CS 594

Application module - the core functionality of the IRC Chat program.

This handles tracking of clients and their associated sockets, sending
and recieving messages, message parsing, and other neccessary functionality.
'''

from email import message
import logging

from app.user import User
from app.chatroom import Chatroom

DEFAULT_ROOM_NAME = '#lobby'


# Broadcast a message to all clients in a given room
def message_broadcast(room, sender_name, message, debug=False):
    '''
    sends a message to all the users in a Chatroom() instance.
    won't send message if a user in that room has blocked the sender!

    parameters
    -----------
    - room = Chatroom() object
    - sender_name = senders name (str)
    - message = message string
    - debug (optional) 
    '''
    if debug:
        logging.info(f'irc.message_broadcast() \nSending message from {sender_name} to room {room.name}: \nMessage: {message}\n')
    # Send the message to all clients in this room, including the sender. Excludes users who blocked sender!
    for client in room.clients:
        if room.clients[client].has_blocked(sender_name):
            continue
        room.clients[client].send(f'{room.name} {sender_name} : {message}'.encode('ascii'))


# The container that has rooms, which have lists of clients
class PyRC:
    '''
    The main IRC chat application. One default room - #lobby - is created when
    this class is instantiated. PyRC() also keeps tracks of current users 
    and their socket info.

    PyRC.message_parser(message:str, user_name, user_socket) is the main point 
    of entry for this application. All message strings recieved from the client 
    should be sent through here.

    Initialize PyRC(debug=True) to create a logger and terminal read outs
    '''
    def __init__(self, debug=False):
        # Debuggin' stuff
        self.debug = debug
        if self.debug:
            logging.basicConfig(filename='PyRC_App.log', 
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
            # self.rooms[DEFAULT_ROOM_NAME].message_all_clients(user_name, join_message)
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
            for room in self.rooms:
                if self.rooms[room].has_user(user_name):
                    self.rooms[room].remove_client_from_room(user_name)
                    self.users[user_name].curr_rooms.remove(room)
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
        rooms = list(self.rooms.keys())
        return " ".join(rooms)
    
    # Check if the room name begins with '#', check if user is already in the room,
    # create the room if it does not exist, then join the room the user specified
    def join_room(self, room_to_join, sender_name):
        '''
        join or create a new Chatroom() instance. 
        
        does not remove a user from a previous room!

        parameters
        --------------
        - room_to_join = '#room_name' OR list['#room_name1', '#room_name2',..]
        - sender_name = ''
        '''
        if self.debug:
            logging.info(f'app.join_room() \nattempting to add {sender_name} to {room_to_join}...\n')

        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            if self.debug:
                logging.info(f'app.join_room() \ncreating {room_to_join}...\n')

            # create new room.
            self.create_room(room_to_join, sender_name)
            self.users[sender_name].send(f'Joined {room_to_join}!'.encode('ascii'))
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
                self.users[sender_name].send('You are already in this room, silly!'.encode('ascii'))

            # add to room
            join_message = f'{sender_name} joined {room_to_join}!'
            self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name])
            if self.debug:
                logging.info(f'\napp.join_room() \n{sender_name} joined {room_to_join}!')
            message_broadcast(self.rooms[room_to_join], sender_name, join_message, self.debug)
            return f'Joined {room_to_join}!'

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
    def leave_room(self, room_to_leave, sender_name):
        '''
        leave a Chatroom() instance. will remove room if it's empty.
        sends user back to last room on their curr_rooms list, or back
        to the #lobby if that's the only other name on the list. 

        parameters
        -------------
        - room_to_leave = '' (key for app.rooms dict)
        - sender_name = ''
        '''
        # case where room doesn't exist
        if room_to_leave not in self.rooms.keys():
            if self.debug:
                logging.error(f'app.leave_room() \nRoom {room_to_leave} doesnt exist!\n')            
            self.users[sender_name].send(f'Error: {room_to_leave} does not exist\n'.encode('ascii'))

        # case where the user isn't in that room
        elif self.rooms[room_to_leave].has_user(sender_name) == False:
            if self.debug:
                logging.info(f'app.leave_room() \nUser {sender_name} isnt in that room!\n')   
            self.users[sender_name].send(f'Error: You are not in {room_to_leave}\n'.encode('ascii'))

        # otherwise leave
        else:
            if self.debug:
                logging.info(f'app.leave_room() \nRemoving {sender_name} from {room_to_leave}...\n')

            # remove user from SINGLE room. doesn't send them anywhere
            # unless they only had #lobby on their list after they left their
            # current room.
            else:
                self.rooms[room_to_leave].remove_client_from_room(sender_name)
                self.users[sender_name].curr_rooms.remove(room_to_leave)
                exit_message = f'{sender_name} left {room_to_leave}!'
                
                # make sure we don't broadcast to an empty room...
                if len(self.rooms[room_to_leave].clients) > 0:
                    message_broadcast(self.rooms[room_to_leave], sender_name, exit_message, self.debug)

                # send user back to previous room if needed
                # user should still get messages from all the rooms they're active in. 
                # this just checks whether there's a discrepancy between their active room list
                # and the actual users in those rooms. 
                # this check (hopefully) won't ever actually be used, it's just an extra failsafe.
                if len(self.users[sender_name].curr_rooms) > 1:
                    prev_room = self.users[sender_name].curr_rooms[-1]
                    # if the user isn't listed as a client in that room for some reason...
                    if sender_name not in self.rooms[prev_room].clients.keys():
                        self.rooms[prev_room].add_new_client_to_room(self.users[sender_name])
                        join_message = f'{sender_name} joined {prev_room}!'
                        message_broadcast(self.rooms[prev_room], sender_name, join_message, self.debug)

                # ...otherwise they'll be in the #lobby by default
                else:
                    ...

    def leave_all(self, sender_name):
        '''
        removes a user from all their active rooms, then returns
        them to #lobby

        parameters
        ------------
        - sender_name = ''
        '''
        # case where user doesn't have any active rooms for some reason
        if len(self.users[sender_name].curr_rooms) == 0:
            if self.debug:
                logging.error(f'app.leave_room() \n{sender_name} not in any active rooms somehow!\n')
            self.users[sender_name].send(f'Error: {sender_name} not in any rooms!'.encode('ascii'))

        # case where user is only active in the lobby
        elif len(self.users[sender_name].curr_rooms) == 1 and DEFAULT_ROOM_NAME in self.users[sender_name].curr_rooms:
            self.users[sender_name].send(f'Error: you are only in {DEFAULT_ROOM_NAME}! \nUse /quit to exit app'.encode('ascii'))

        # iterate through users curr_rooms list
        else:
            rooms_left = [] # this will be used to update users list afterwards
            for room in range(len(self.users[sender_name].curr_rooms)):
                # make sure they don't get removed from the #lobby!
                if self.users[sender_name].curr_rooms[room] == DEFAULT_ROOM_NAME:
                    continue
                room_to_leave = self.users[sender_name].curr_rooms[room]
                rooms_left.append(room_to_leave)

                self.rooms[room_to_leave].remove_client_from_room(sender_name)
                leave_message = f'{sender_name} left {room_to_leave}!'
                message_broadcast(self.rooms[room_to_leave], sender_name, leave_message, self.debug) 
            
            # update curr_rooms list
            for room in rooms_left:
                self.users[sender_name].curr_rooms.remove(room)
 
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
            # remove command and username arguments, then send message text
            message_text = message.split()
            message_text = message_text[2:]
            message_text = f'/whisper @{sender_name}: {" ".join(message_text)}'
            if self.debug:
                logging.info(f'app.message_parser() /whisper \{sender_name} sending message to {receiver} \nmessage: {message_text}\n')
            # send message to receiver
            self.users[receiver].send(message_text.encode('ascii'))

    # directly message another user
    def send_dm(self, sender, message, receiver):
        '''
        directly message another user. this should be called by sender.

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

        - /create #room_name
            - createa a new chatroom. 
            - will only create it if the name hasn't been used

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
        '''
        if self.debug:
            logging.info(f"app.message_parser() \nsender sock: {sender_socket} \nsender_name: {sender_name} \nmessage: {message} \nmessage as word list: {message.split()}\n")

        # send message to each room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            for room in self.users[sender_name].curr_rooms:
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
            # NOTE: iterate through room dicts and check keys for current room!
            elif message.split()[1] == self.users[sender_name].curr_room:
                sender_socket.send(f'Error: you are already in {message.split()[1]}!')
                return f'Error: you are already in {message.split()[1]}!'
            
            # otherwise try to join or create room(s).
            else:
                # check if there's more than one room argument
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
                            sender_socket.send(f'You are already in {rooms_to_join[room]}!'.encode('ascii'))
                else:
                    if self.debug:
                        logging.info(f'app.message_parser() /join \nattempting to join {message.split()[1]}...\n')
                    # add conditon to check whether user is in this room here too...
                    self.join_room(message.split()[1], sender_name, sender_socket)

        ### Case where user wants to create a new room ###
        elif message.split()[0] == '/create':
            '''
            syntax: /create #room_name
            '''
            # case where user forgets to add a room name
            if len(message.split()) == 1:
                if self.debug:
                    logging.info(f'app.message_parser() /create \n{sender_name} sent /create command without arg')
                sender_socket.send(f'Error: must include a roomname argument separated with a space \nex: /create #room_name'.encode('ascii'))
                return f'Error: must include a room name argument separated with a space \nex: /create #room_name'

            # case where room_name doesn't start with a '#'
            elif '#' not in message.split()[1]:
                if self.debug:
                    logging.info(f'app.message_parser() /create \n{message.split()[1]} did not contain a # to denote a room name')
                sender_socket.send(f'Error: must include a "#" when denoting a room name! \nex: /create #room_name'.encode('ascii'))
                return f'Error: must include a "#" when denoting a room name! \nex: /create #room_name'                 

            # case where room already exists
            elif message.split()[1] in self.rooms.keys():
                if self.debug:
                    logging.info(f'app.message_parser() /create \n{message.split()[1]} already exists!')
                sender_socket.send(f'Error: {message.split()[1]} already exists!'.encode('ascii'))
                return f'Error: {message.split()[1]} already exists!'

            # otherwise create a new room
            else:
                if self.debug:
                    logging.info(f'app.message_parser() /create \ncreating {message.split()[1]}...')
                self.create_room(message.split()[1], sender_name)

        ### Case where user wants to leave a room ###:
        elif message.split()[0] == "/leave":
            '''
            syntax: /leave #room OR /leave all
            '''
            # Case where user just submits "/leave"
            if len(message.split()) == 1:
                if self.debug:
                    logging.info(f'app.message_parser() /leave \nSending /leave error message to socket: \n {sender_socket}\n')
                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))

            # case where user wants to leave ALL their active rooms
            elif message.split()[1] == 'all':
                self.leave_all(sender_name)

            # otherwise try to remove from single room
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
                    self.leave_room(room_to_leave, sender_name)

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
            '''NOTE: iterate through app.rooms.clients to check each possible room for user'''
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
            '''
            syntax: /broadcast #room1 <message> / #room2 <message> / ...
            
            remove /broadcast command 
            message.pop(0)

            TODO: implement!

            NOTE: there's now chatroom.message_all_clients(sender, message)!
                  this will be usefull with iterating through PyRC.rooms
                  will need to chekc whether chatroom.clients is empty or not first

            NOTE: need to make sure the #room_name and message are bundled together,
                  and that if someone were to include a '#' in their message that it wouldn't
                  break the message apart!

                  is there a way to store user's input in a dictionary with the room as the key
                  and the value as the message? 

                  first remove /broadcast command (message.pop(0)), then parse for room names 
                  and messages 

            NOTE: is there a way to get looped input from a user from a server? look into this!
                  might be a lot simpler than trying to parse one long message! 

                    broadcast/

                    response: which rooms do you want to broadcast to?
                    -> list all active rooms

                    /broadcast #room_name1 <message1>
                    /broadcast #room_name2 <message2>

                    etc...
                
                loop:
                    get room name, check if there's people in it
                        
                        if yes parse message: 

                            loop:
                                append individual words to message list 

                                check for deliminator '/' to denote end of message!
                                must have a whitespace on either side!
                                
                                check if '/' is accidentally stuck to the last letter of the
                                last word in the message before another #room_name is 
                                listed?

                                    check if any words starting with '#' are active rooms
                                    in the server!

                                    if word1[-1:] == '/' and word2[0] == '#' and word2 in app.rooms.keys()
                    
                            send message to #room_name

                        else, skip 
            '''

        ### Case where user wants to directly message another user ###
        elif message.split()[0] == "/message":
            '''
            syntax - /message @<user_name> <message>
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
                '''
                NOTE: look into a way to do the pop/.join stuff
                      using list slicing instead. 
                      seems like a lot of unnecessary steps here.
                '''
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
            '''
            syntax: /whisper @<user_name>
            '''    

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
                '''
                NOTE: look into a way to do the pop/.join stuff
                      using list slicing instead. 
                      seems like a lot of unnecessary steps here.
                '''
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