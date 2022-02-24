'''
user class module
'''

import logging

class User:
    '''
    User class. Keeps track of a user's name, current room, and 
    their socket() object.

    Also handles direct message functionality (both asynchronous and not), 
    and blocking/unblocking other users.
    '''

    def __init__(self, name, socket, curr_room, debug=False):
        # debuggin' stuff..
        self.debug = debug           
        if self.debug:
            logging.basicConfig(filename='IRC_User.log', 
                                filemode='w', 
                                level=logging.DEBUG, 
                                format='%(asctime)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p')

        self.name = name                # username
        self.socket = socket            # user's socket() object
        self.curr_room = curr_room      # user's current room (str)
                                        # NOTE: replace self.curr_room with curr_rooms = []!
        self.curr_rooms = [curr_room]   # list (list[str]) of room names user is active in
        
        self.blocked = []               # list of blocked users (list[str])
        self.dms = {}                   # dictionary of direct messages. 
                                        # key is sender (str), value is the message (str)

    def send(self, message):
        '''
        send a message via this user's socket object.
        ***message must be a string already encoded to ascii!***
        '''
        if self.debug:
            logging.info(f'user.send() user: {self.name} \nsending encoded ascii message: {message} \nvia socket: \n{self.socket}\n')
        if type(message) != bytes:
            if self.debug:
                logging.error(f'user.send() \nuser: {self.name} \nERROR: message not in correct format! \
                                Must be a series of bytes using ascii encoding. \nReceived: {message} \nType: {type(message)}\n')
            self.socket.send(f'Error: message not in correct format! Must be a series of bytes using ascii encoding.'.encode('ascii'))
        self.socket.send(message)

    def get_dm(self, sender, message):
        '''
        ability to receive DM's from another user.
        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key
        '''
        # is this sender blocked?
        if sender not in self.blocked:
            # store the message if we haven't gotten one from this user
            if sender not in self.dms.keys():
                self.dms[sender] = message
            # otherwise add to their list of messages
            else:
                self.dms[sender].extend(message)
            if self.debug:
                logging.info(f'user.get_dm() \n{sender} sent message {message}\n')
            # send an alert message to receiver
            self.send(f'New message from {sender}! \nUse /dms @{sender} to read'.encode('ascii'))
        else:
            ...

    def read_dm(self, user):
        '''
        displays a message from a single user
        '''
        if len(self.dms) > 0:
            if user in self.dms.keys():
                if self.debug:
                    logging.info(f'user.read_dm() \nsender: {user} \nmessage: {self.dms[user]}\n')
                self.send(f'{user}: \n{self.dms[user]}'.encode('ascii'))
                return f'{user}: \n{self.dms[user]}'
            else:
                if self.debug:
                    logging.error(f'user.read_dm() \nERROR: no messages from user: {user}!\n')
                self.send(f'No messages from {user}!\n'.encode('ascii'))
                return f'No messages from {user}!'
        else:
            if self.debug:
                logging.info('user.read_dm() \nNo messages!\n')
            self.send('No messages!'.encode('ascii'))
            return 'No messages!'

    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users. 
        '''
        dms = []
        if len(self.dms) > 0:
            for sender in self.dms:
                dms.append(f'{sender} : \n{self.dms[sender]}\n')
            dms_str = ' '.join(dms)
            if self.debug:
                logging.info(f'user.read_all_dms() \nuser: {self.name} \nmessages: {dms_str}\n')
            self.send(dms_str.encode('ascii'))
            return dms_str
        else:
            self.send('No direct messages!'.encode('ascii'))
            return 'No direct messages!'
    
    def has_blocked(self, sender):
        '''
        finds out whether a given user has been blocked by this user
        '''
        return True if sender in self.blocked else False

    def block(self, sender):
        '''
        block a user
        '''
        if sender not in self.blocked:
            self.blocked.append(sender)
            self.send(f'{sender} has been blocked!'.encode('ascii'))
        else:
            self.send(f'{sender} is already blocked.'.encode('ascii'))
    
    def unblock(self, sender):
        '''
        unblock another user.
        '''
        if sender in self.blocked:
            self.blocked.remove(sender)
            self.send(f'{sender} has been unblocked!'.encode('ascii'))
        else:
            self.send(f'{sender} was not blocked.'.encode('ascii'))
