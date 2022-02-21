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

        self.name = name             # username
        self.socket = socket         # user's socket() object
        self.curr_room = curr_room   # user's current room (str)
        
        self.blocked = []            # list of blocked users (list[str])
        self.dms = {}                # dictionary of direct messages. 
                                     # key is sender (str), value is the message (str)

    def send(self, message):
        '''
        send a message via this user's socket object.
        ***message must be a string already encoded to ascii!***
        '''
        if self.debug:
            print(f'\nuser.send() user: {self.name} \nsending encoded ascii message: {message} \nvia socket: \n{self.socket}')
            logging.info(f'user.send() user: {self.name} \nsending encoded ascii message: {message} \nvia socket: \n{self.socket}\n')
        self.socket.send(message)

    def get_dm(self, sender, message):
        '''
        ability to receive DM's from another user.
        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key
        '''
        # is this sender blocked?
        if sender not in self.blocked:
            # store the message
            self.dms[sender] = message
            if self.debug:
                print(f'user.get_dm() \n{sender} sent message {message}')
                logging.info(f'user.get_dm() \n{sender} sent message {message}\n')
            # send an alert message to receiver
            self.send(f'New message from {sender}! \nUse /dms @{sender} to read'.encode('ascii'))
        else:
            ...

    def read_dm(self, sender):
        '''
        displays a message from a single user
        '''
        if len(self.dms) > 0:
            if sender in self.dms.keys():
                if self.debug:
                    logging.info(f'user.read_dm() \nsender: {sender} \nmessage: {self.dms[sender]}\n')
                self.send(f'{sender}: \n{self.dms[sender]}'.encode('ascii'))
            else:
                if self.debug:
                    logging.error(f'user.read_dm() \nERROR: no messages from user: {sender}!\n')
                self.send(f'No messages from {sender}!\n'.encode('ascii'))
        else:
            if self.debug:
                logging.info('user.read_dm() \nNo messages!\n')
            self.send('No messages!'.encode('ascii'))

    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users. 
        '''
        dms = []
        if len(self.dms) > 0:
            for sender in self.dms:
                dms.append(f'{sender} : \n{self.dms[sender]}')
            dms_str = ''.join(dms)
            if self.debug:
                print(f'\nuser.read_all_dms() \nuser: {self.name} \nmessages: {dms_str}')
                logging.info(f'user.read_all_dms() \nuser: {self.name} \nmessages: {dms_str}\n')
            self.send(dms_str.encode('ascii'))
        else:
            self.send('No direct messages!'.encode('ascii'))
    
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
