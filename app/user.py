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
        self.socket.send(message)

    def receive_dm(self, sender, message):
        '''
        ability to receive DM's from another user.
        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key
        '''
        # are there messages from sender?
        if sender not in self.blocked:
            # store the message
            self.dms[sender] = message
            # send an alert message
            self.send(f'New message from {sender}! \nUse /dms {sender} to read'.encode('ascii'))
        else:
            self.send(f'{sender} is blocked!'.encode('ascii'))

    def read_dm(self, sender):
        '''
        displays a message from a single user
        '''
        if len(self.dms) > 0:
            if sender in self.dms.keys():
                self.send(f'{sender}: \n{self.dms[sender]}\n'.encode('ascii'))
            else:
                self.send(f'No messages from {sender}!\n'.encode('ascii'))
        else:
            self.send(f'No messages!'.encode('ascii'))

    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users. 
        '''
        dms = []
        if len(self.dms) > 0:
            for sender in self.dms:
                dms.append(f'{sender} : {self.dms[sender]}\n')
            dms_str = dms.join(" \n")
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
