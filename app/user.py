'''
user class module
'''

import logging

DEBUG = False
if DEBUG:
    logging.basicConfig(filename='IRC_User.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')
class User:
    '''
    user class. keeps track of a user's name and socket.
    also handles direct message functionality, and blocking/unblocking
    other users.

    TODO: add /whisper option for direct messages between a single other user
    '''

    def __init__(self, name, socket, curr_room, debug=False):
        self.debug = debug           # debuggin' stuff..

        self.name = name             # username
        self.socket = socket         # user's socket() object
        self.curr_room = curr_room   # user's current room (str)
        self.blocked = []            # list of blocked users (list[str])
        self.dms = {}                # dictionary of direct messages. 
                                     # key is sender, value is the message

    def send(self, message):
        '''
        send a message via this user's socket object.
        '''
        self.socket.send(message)

    def get_dm(self, sender, message):
        '''
        ability to recieve DM's from another user.
        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key
        '''
        if sender not in self.blocked:
            # are there messages from sender?
            if sender in self.dms.keys():
                self.dms[sender] = message
                self.socket.send(f'{sender}: {message}'.encode('ascii'))
            else:
                self.socket.send(f'No messages from {sender}'.encode('ascii'))
        else:
            self.socket.send(f'{sender} is blocked!'.encode('ascii'))
    
    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users. 
        '''
        dms = []
        if len(self.dms) > 0:
            for sender in self.dms:
                dms.append(f'{sender} : {self.dms[sender]}\n')
            dms_str = dms.join()
            self.socket.send(dms_str.encode('ascii'))
        else:
            self.socket.send('No direct messages'.encode('ascii'))

    def read_dm(self, sender):
        '''
        displays a message from a single user
        '''
        if len(self.dms) > 0:
            if sender in self.dms.keys():
                self.socket.send(f'{sender}: \n{self.dms[sender]}\n'.encode('ascii'))
            else:
                self.socket.send(f'No messages from {sender}!\n'.encode('ascii'))
    
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
            self.socket.send(f'{sender} has been blocked.'.encode('ascii'))
        else:
            self.socket.send(f'{sender} is already blocked.'.encode('ascii'))
    
    def unblock(self, sender):
        '''
        unblock another user.
        '''
        if sender in self.blocked:
            self.blocked.pop(sender)
            self.socket.send(f'{sender} has been unblocked!'.encode('ascii'))
        else:
            self.socket.send(f'{sender} was not blocked!'.encode('ascii'))
