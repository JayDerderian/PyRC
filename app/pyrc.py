'''
Jay Derderian
CS 594

Application module - the core functionality of the PyRC Chat program.
'''

from numpy import reciprocal
from app.user import User
from app.chatroom import Chatroom

DEFAULT_ROOM_NAME = '#lobby'


# Broadcast a message to all clients in a given room
def message_broadcast(room, sender_name, message):
    '''
    sends a message to all the users in a Chatroom() instance.
    won't send message if a user in that room has blocked the sender!

    parameters
    -----------
    - room = Chatroom() object
    - sender_name = '' senders name (str)
    - message = '' message string
    '''
    # Send the message to all clients in this room, including the sender. 
    # Excludes users who blocked sender, or users who muted this room!
    for client in room.clients:
        if room.clients[client].has_blocked(sender_name):
            continue
        elif room.clients[client].has_muted(room.name):
            continue
        room.clients[client].send(f'{room.name} {sender_name} : {message} '.encode('ascii'))


# PyRC class. 
# Manages chatrooms and enables certain functionalities between users.
class PyRC:
    '''
    The main IRC chat application. One default room - #lobby - is created when
    this class is instantiated. PyRC() also keeps tracks of current users 
    and their socket info.

    PyRC.message_parser() is the main point of entry for this application. 
    All message strings recieved from the client should be sent through here.
    '''
    def __init__(self):

        # Dictionary of active rooms. 
        # Key is room name (str), value is the Chatroom() object. 
        # #lobby room is always present by default, even if its empty.
        self.rooms = {}
        self.rooms[DEFAULT_ROOM_NAME] = Chatroom(room_name = DEFAULT_ROOM_NAME) 

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
                                         socket = new_user_socket)
            # add them to default lobby.
            self.rooms[DEFAULT_ROOM_NAME].add_new_client_to_room(self.users[user_name])
            join_message = f'{user_name} joined {DEFAULT_ROOM_NAME}!'
            # send join message to room
            message_broadcast(self.rooms[DEFAULT_ROOM_NAME], user_name, join_message)
            return True

        # case where they're already in the instance
        else:
            new_user_socket.send(f'{user_name} is already in this instance!'.encode('ascii'))
            return False

    # remove a user from the instance
    def remove_user(self, user_name):
        '''
        remove a user from app instance

        parameters
        -----------
        - user_name = ''
        '''
        if user_name in self.users.keys():
            # this could iterate over lots of rooms that don't have
            # this user, but it will make sure the user is definitively
            # removed in the off chance their curr_rooms list is inaccurate.
            for room in self.rooms:
                if self.rooms[room].has_user(user_name):
                    self.rooms[room].remove_client_from_room(user_name) 
            del self.users[user_name]
        else:
            return f'{user_name} is not in the server!'
    
    # get a list of active users in a specific room
    def get_users(self, room, sender_socket):
        '''
        get all active users in a specified room.
        '''
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

    # returns true or false if a room exists
    def is_room(self, room_name):
        '''
        is this an active room?
        '''
        return True if room_name in self.rooms.keys() else False

    # returns a list of active rooms
    def list_all_rooms(self):
        '''
        returns a str of all active rooms.
        '''
        rooms = list(self.rooms.keys())
        return " ".join(rooms)

    # get a list of rooms a user is active in
    def list_my_rooms(self, sender_name):
        '''
        returns a str of rooms a user is active in
        '''
        room_list = self.users[sender_name].curr_rooms
        room_list = " ".join(room_list)
        self.users[sender_name].send(room_list.encode('ascii'))
        return room_list
    
    # Check if the room name begins with '#', check if user is already in the room,
    # create the room if it does not exist, then join the room the user specified
    def join_room(self, room_to_join, sender_name):
        '''
        join or create a new Chatroom() instance. 

        parameters
        --------------
        - room_to_join = '#room_name' OR list['#room_name1', '#room_name2',..]
        - sender_name = ''
        '''
        # Case where this room doesn't already exist
        if room_to_join not in self.rooms.keys():
            # create new room.
            self.create_room(room_to_join, sender_name)
            self.users[sender_name].send(f'Joined {room_to_join}!'.encode('ascii'))
            return f'Joined {room_to_join}!'

        # Case where it DOES already exist
        else:
            # Case where the user is already there
            if self.rooms[room_to_join].has_user(sender_name):
                self.users[sender_name].send(f'You are already in {room_to_join}, silly!'.encode('ascii'))
                return f'You are already in {room_to_join}, silly!'
            # otherwise join the room...
            else:
                self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name])
                join_message = f'{sender_name} joined {room_to_join}!'
                message_broadcast(self.rooms[room_to_join], sender_name, join_message)
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
        self.rooms[room_to_join] = Chatroom(room_name = room_to_join)
        self.rooms[room_to_join].add_new_client_to_room(self.users[sender_name]) 

        # send join message
        join_message = f'{sender_name} joined {room_to_join}!'
        message_broadcast(self.rooms[room_to_join], sender_name, join_message)

    # Check if the room exists, check if user is in the room,
    # remove user from room and delete room if it is empty
    def leave_room(self, room_to_leave, sender_name):
        '''
        leave a Chatroom() instance.

        sends user back to last room on their curr_rooms list, or back
        to the #lobby if that's the only other name on the list. 

        parameters
        -------------
        - room_to_leave = '' (key for app.rooms dict)
        - sender_name = ''
        '''
        # case where room doesn't exist
        if room_to_leave not in self.rooms.keys():          
            self.users[sender_name].send(f'Error: {room_to_leave} does not exist\n'.encode('ascii'))

        # case where the user isn't in that room
        elif self.rooms[room_to_leave].has_user(sender_name) == False:  
            self.users[sender_name].send(f'Error: You are not in {room_to_leave}\n'.encode('ascii'))

        # case where user tries to leave #lobby (default room)
        elif room_to_leave == DEFAULT_ROOM_NAME:
            self.users[sender_name].send(f'Error: {DEFAULT_ROOM_NAME} cannot be left! \nUse /quit to exit.'.encode('ascii'))

        # otherwise leave
        else:
            # remove user from SINGLE room. doesn't send them anywhere
            # unless they only had #lobby on their list after they left their
            # current room.
            self.rooms[room_to_leave].remove_client_from_room(sender_name)
            self.users[sender_name].curr_rooms.remove(room_to_leave)
            exit_message = f' {sender_name} left {room_to_leave}!'
            
            # make sure we don't broadcast to an empty room...
            if len(self.rooms[room_to_leave].clients) > 0:
                message_broadcast(self.rooms[room_to_leave], sender_name, exit_message)

            # send user back to previous room 
            # user should still get messages from all the rooms they're active in. 
            if len(self.users[sender_name].curr_rooms) > 1:
                prev_room = self.users[sender_name].curr_rooms[-1]
                self.rooms[prev_room].add_new_client_to_room(self.users[sender_name])
                join_message = f'{sender_name} joined {prev_room}!'
                message_broadcast(self.rooms[prev_room], sender_name, join_message)

            # ...otherwise they'll be in the #lobby by default
            else:
                ...

    # leave all rooms except #lobby
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
                leave_message = f' {sender_name} left {room_to_leave}!'
                self.users[sender_name].send(leave_message.encode('ascii'))
                message_broadcast(self.rooms[room_to_leave], sender_name, leave_message)
                 
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
        #pop @ from name
        receiver = self.parse_user_name(receiver)
        # case where receiver is not in app instance
        if receiver not in self.users:                  
            self.users[sender_name].send(f'Error: {receiver} not in server!'.encode('ascii'))

        # case where receiver blocked sender
        elif self.users[receiver].has_blocked(sender_name):
            self.users[sender_name].send(f'Error: you were blocked by {receiver}!'.encode('ascii'))

        # otherwise, try to send whisper
        else:
            message_text = f'/whisper @{sender_name}: {message}'
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
            self.users[sender].send(f'Error: {receiver} not in app instance!'.encode('ascii'))
        else:
            # save message to User() instance. 
            # User() will send notification message to receiver.
            # User() will also check whether sender was blocked by receiver.
            self.users[receiver].get_dm(sender, message)

    # read direct messages
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
        '''
        self.users[user_name].block(to_block)

    # unblock a user
    def unblock(self, user_name, to_unblock):
        '''
        unblocks a user. 
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

        messages should, by default, go out to the rooms the user is currently in.
        no need for a #room_name specification. 

        #lobby is the default room that any user can be in at any given time, 
        and is where new users are sent to when they first join the app instance.

        commands
        ----------

        - (No command) <message>
            - Send message to all active rooms. #lobby is the default room.

        - /rooms
            - list all currently active rooms in app instance

        - /myrooms
            - list all rooms a user is active in

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

        - /mute #room1 (opt) #room2...
            - mutes output from selected rooms that you're active in

        - /unmute #room1 (opt) #room2...
            - unmutes output from selected rooms

        - /users
            - list all other users in the room the client is currently in

        - /broadcast #room_name1 : <message_1> / #room_name2 : <message_2>...
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
            - directly message another user in real-time.

        - /block <user_name>
            - block DM's from other users

        - /unblock <user_name>
            - unblocks a user

        - /help
            - displays a list of available commands

        - /clear
            - clear console screen.

        - /quit
            - leave current instance.

        NOTE: /quit, /clear, and /help are handled on the client side!
        '''
        # send message to each room the user is currently in. 
        # this just checks whether there's a command prior to the message
        if message[0] != '/':
            for room in self.users[sender_name].curr_rooms:
                message_broadcast(self.rooms[room], sender_name, message)

        ### Case where user wants to join a room ###:
        elif message.split()[0] == '/join':
            '''
            syntax : /join #room_name1 (opt) #room_name2 etc...
            '''
            # case where there's a typo or user forgot to add a room argument
            if len(message.split()) < 2:
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode('ascii'))
                return "/join requires a #room_name argument.\nPlease enter: /join #roomname\n"

            # case where first room arg doesn't have '#' symbol in front of it
            elif '#' not in message.split()[1]:
                sender_socket.send("/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n".encode('ascii'))
                return "/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n"
            
            # case where a random word follows the roomname (i.e. /join #roomname t)
            elif len(message.split()) == 3:
                if message.split()[2][0] != '#':
                    sender_socket.send('Error: incorrect syntax! all room names must start with a "#"'.encode('ascii'))
                    return 'Error: incorrect syntax! all room names must start with a "#"'
            
            # otherwise try to join or create room(s).
            else:
                # check if there's more than one room arguments 
                # if so, join multiple rooms 
                if len(message.split()) > 2:
                    rooms_to_join = []
                    for word in message.split():
                        if word[0] == '#':
                            rooms_to_join.append(word)
                    # attempt to add user to these rooms
                    for room in rooms_to_join:
                        self.join_room(room, sender_name)
                # otherwise join single room
                else:
                    self.join_room(message.split()[1], sender_name)

        ### Case where user wants to create a new room ###
        elif message.split()[0] == '/create':
            '''
            syntax: /create #room_name
            '''
            # case where user forgets to add a room name
            if len(message.split()) == 1:
                sender_socket.send(f'Error: must include a roomname argument separated with a space \nex: /create #room_name'.encode('ascii'))
                return f'Error: must include a room name argument separated with a space \nex: /create #room_name'

            # case where room_name doesn't start with a '#'
            elif '#' not in message.split()[1]:
                sender_socket.send(f'Error: must include a "#" when denoting a room name! \nex: /create #room_name'.encode('ascii'))
                return f'Error: must include a "#" when denoting a room name! \nex: /create #room_name'                 

            # case where room already exists
            elif message.split()[1] in self.rooms.keys():
                sender_socket.send(f'Error: {message.split()[1]} already exists!'.encode('ascii'))
                return f'Error: {message.split()[1]} already exists!'

            # otherwise create a new room
            else:
                self.create_room(message.split()[1], sender_name)

        ### Case where user wants to leave a room ###:
        elif message.split()[0] == "/leave":
            '''
            syntax: /leave #room OR /leave all
            '''
            # Case where user just submits "/leave"
            if len(message.split()) == 1:
                sender_socket.send("/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n".encode('ascii'))
                return "/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n"

            # case where user wants to leave ALL their active rooms
            elif message.split()[1] == 'all':
                self.leave_all(sender_name)

            # otherwise try to remove from single room
            else:
                room_to_leave = message.strip().split()[1]
                # case where user forgets to include "#" in "#room_name"
                if room_to_leave[0] != "#":
                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode('ascii'))
                    return "/leave requires a #roomname argument to begin with '#'.\n"
                # leave room...
                else:
                    sender_socket.send(f'Leaving {room_to_leave}...'.encode('ascii'))
                    # this sends the user back to the #lobby!
                    self.leave_room(room_to_leave, sender_name)

        ### Case where user wants to list all active rooms ###
        elif message.split()[0] == "/rooms":
            if len(self.rooms) > 0:
                rooms = f'Active rooms: \n{self.list_all_rooms()}'
                sender_socket.send(rooms.encode('ascii'))
            else:
                sender_socket.send('Error: no active rooms!'.encode('ascii'))

        ### Case where a user wants a list of all their active rooms ###
        elif message.split()[0] == '/myrooms':
            self.list_my_rooms(sender_name)

        ### Case where user wants list of other users in their current room ###
        elif message.split()[0] == "/users":
            '''
            syntax: /users #room_name
            '''
            # case where user forgets to add a room name argument
            if len(message.split()) == 1:
                sender_socket.send('Error: /users requires a room name argument \nex: /users #room_name'.encode('ascii'))
            # case where room_name doesn't start with a '#'
            elif '#' not in message.split()[1]:
                sender_socket.send('Error: room name arg must start with "#" \nex: /users #room_name'.encode('ascii'))
            else:
                room = message.split()[1]
                # case where the room doesn't actually exist
                if room not in self.rooms.keys():
                    sender_socket.send(f'Error: {room} doesnt exist!'.encode('ascii'))
                # send user list
                else:
                    sender_socket.send(f'{room} users: {self.rooms[room].get_users()}'.encode('ascii'))

        ### Case where user wants to send *distinct* messages to *multiple* rooms ###
        elif message.split()[0] == '/broadcast':
            '''
            syntax: /broadcast #room1 : <message> / #room2 : <message> / ...
            '''
            # case where user forgets args
            if len(message.split()) == 1:
                sender_socket.send('Error: must include at least one room name and messsage! \nex: /broadcast #room_name : <message> /'.encode('ascii'))
                return 'Error: must include at least one room name and messsage! \nex: /broadcast #room_name : <message> /'
            
            # case where user doesn't include a message
            elif len(message.split()) == 2:
                sender_socket.send('Error: must include a message! \nex: /broadcast #room_name : <message> /'.encode('ascii'))
                return 'Error: must include a message! \nex: /broadcast #room_name : <message> /'

            # case where message doesn't end with a '/'
            elif message.split()[-1] != '/':
                sender_socket.send('Error: all messages must end with a "/" to denote ending. \nex: /broadcast #room_name : <message> /'.encode('ascii'))
                return 'Error: all messages must end with a "/" to denote ending. \nex: /broadcast #room_name : <message> /'

            # otherwise, try to parse
            else:
                message_ = message.split()
                # remove /broadcast command
                message_.pop(0)
                # get room name, then save each word to message list 
                # "Rooms" = list of rooms (list[str]), "Messages" = list individual messages (list[str])
                messages = {"Rooms": [], "Messages": []}
                word = 0
                while word < len(message_):
                    # is this a room name?
                    if message_[word][0] == '#' and message_[word + 1] == ':':
                        messages['Rooms'].append(message_[word])
                        word += 1
                    # skip ':'
                    elif message_[word] == ':':
                        word += 1 
                    # else, keep adding words until we reach '/'
                    else:
                        # start at current place in iteration
                        w = word 
                        message_text = []
                        # retreive the message for *this* room
                        while w < len(message_):
                            if message_[w] == '/': # have we reached the end of the message?
                                break
                            elif message_[w][-1] == '/': # did the user accidentally attach '/' to the last word?
                                # remove /, then add to list
                                wrd = list(message_[w]).remove('/')
                                wrd = " ".join(wrd)
                                message_text.append(wrd)
                                # is the next word a room name? 
                                # if so, break since this was clearly a typo
                                # also trying to avoid an index error.
                                if  w < len(message_) and message_[w + 1][0] == '#': 
                                    break # exit loop since this was meant to denote the end of the message
                            else:
                                message_text.append(message_[w])
                            w += 1
                        messages["Messages"].append(" ".join(message_text))
                        word = w + 1 # update outer loop placement so we don't keep recopying the messages

                # make sure the total number of room names equals the total number of messages
                if len(messages['Rooms']) != len(messages['Messages']):
                    sender_socket.send('Error: unequal amounts of rooms and messages!'.encode('ascii'))
                    return 'Error: unequal amounts of rooms and messages!'
                else:
                    # send each message to each room
                    for item in range(len(messages['Rooms'])):
                        # get current room, send message
                        rm = messages["Rooms"][item]
                        msg = " ".join(messages["Messages"][item])
                        if self.is_room(rm):
                            message_broadcast(self.rooms[rm], sender_name, msg)
                        else:
                            sender_socket.send(f'Error: {rm} doesnt exist!'.encode('ascii'))

                return messages

        ### Case where user wants to mute some of their active rooms ###
        elif message.split()[0] == '/mute':
            '''
            syntax: /mute #room1 #room2
            '''
            # case where user forgets #
            if '#' not in message.split()[1]:
                sender_socket.send('Error: command must start with a /!'.encode('ascii'))
            # case where user forgets first arg
            elif len(message.split()) == 1:
                sender_socket.send('Error: must include at least one room name argument. \nex: /mute #roomname'.encode('ascii'))
            # mute room(s)
            else:
                message_ = message.split()
                for word in message_:
                    # make sure this is actually a room name
                    if word[0] == '#' and word in self.rooms.keys():
                        self.users[sender_name].mute(word)
    
        ### Case where a user wants to unmute some of their active rooms
        elif message.split()[0] == '/unmute':
            '''
            syntax: /unmute #room1 #room2... -or- /unmute all
            '''
            # case where user forgets first arg
            if len(message.split()) == 1:
                sender_socket.send('Error: must include at least one room name argument. \nex: /mute #roomname'.encode('ascii'))
            # case where user forgets # and the second arg isn't 'all'
            elif len(message.split()) == 2 and '#' not in message.split()[1] and message.split()[1] != 'all':
                sender_socket.send('Error: room name must start with a "#"! \nex: /unmute #roomname'.encode('ascii'))
            # otherwise unmute the room(s)...
            else:
                # Unmute *all* muted rooms for this user or n amount of specified rooms
                if message.split()[1] == 'all' or message.split().count('#') > 1:
                    message_ = message.split()
                    for word in message_:
                        # make sure this is actually a room name
                        if word[0] == '#' and word in self.rooms.keys():
                            self.users[sender_name].unmute(word)
                            sender_socket.send(f'{word} has been unmuted!'.encode('ascii'))
                # unmute *one* room
                else:
                    room = message.split()[1]
                    self.users[sender_name].unmute(room)

        ### Case where user wants to directly message another user ###
        elif message.split()[0] == "/message":
            '''
            syntax - /message @<user_name> <message>
            '''
            # case where client doesn't include a user_name
            if len(message.split()) == 1:
                sender_socket.send('Error: /message requires a username argument. \nex: /message @<user_name> <message>'.encode('ascii'))
                return 'Error: /message requires a username argument. \nex: /message @<user_name> <message>'
            # case where user tries to message more than one person at a time.
            elif list(message).count('@') > 1:
                sender_socket.send('Error: /message only takes one username argument. \nex: /message @<user_name> <message>'.encode('ascii'))
                return 'Error: /message only takes one username argument. \nex: /message @<user_name> <message>'
            # get receiver's name then send message
            else:
                receiver = self.parse_user_name(message.split()[1]) # get receiver's name
                message_text = ' '.join(message.split()[2:])        # get message text                
                # send dm
                self.send_dm(sender_name, message_text, receiver)
                
        ### Case where a user wants to check their direct messages ###
        elif message.split()[0] == "/dms":
            '''
            syntax - /dms (opt) @<sender_name> 
            '''
            # check if there's a specific user they're looking for
            if len(message.split()) > 1:
                dm_sender = message.split()[1]
                if dm_sender[0] == '@':
                    # remove @ symbol
                    dm_sender = self.parse_user_name(dm_sender)
                    # get dm's
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
            # case where there's no username or text argument
            if len(message.split()) == 1:
                sender_socket.send('Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'.encode('ascii'))
                return 'Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'

            # case where we try to message more than one user
            elif list(message).count('@') > 1:
                sender_socket.send('Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'.encode('ascii'))
                return 'Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'

            # otherwise, get receiver name and send to method
            else:
                # get receiver's name, then message text
                message_ = message.split()
                message_.pop(0)  # get rid of command
                receiver = message_[0]
                message_.pop(0)  # get rid of receiver name
                self.send_whisper(sender_name, " ".join(message_), receiver)

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