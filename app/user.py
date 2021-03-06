'''
user class module
'''

class User:
    '''
    User class. Keeps track of a user's name, current rooms, and 
    their socket() object.

    Also handles direct message functionality (both asynchronous and not), 
    and blocking/unblocking other users.
    '''

    def __init__(self, name, socket, curr_room):

        self.name = name                # user name
        self.socket = socket            # user's socket() object
        self.curr_rooms = [curr_room]   # list (list[str]) of room names user is active in
        self.muted_rooms = []           # list of muted rooms
        self.blocked = []               # list of blocked users (list[str])
        self.dms = {}                   # dictionary of direct messages. 
                                        # key is sender (str), value is the message (str)

    def send(self, message):
        '''
        send a message via this user's socket object.
        ***message must be a string already encoded to ascii!***

        always preceed with if User.has_blocked(sender) == False !!
        '''
        if type(message) != bytes:
            self.socket.send(f'Error: message not in correct format! Must be a series of bytes using ascii encoding.'.encode('ascii'))
        else:
            self.socket.send(message)

    def has_muted(self, room):
        '''
        was this room muted?
        '''
        return True if room in self.muted_rooms else False
    
    def mute(self, room):
        '''
        mute a room
        '''
        if room not in self.muted_rooms:
            self.muted_rooms.append(room)
    
    def unmute(self, room):
        '''
        unmute a room
        '''
        if room in self.muted_rooms:
            self.muted_rooms.remove(room)

    def get_dm(self, sender, message):
        '''
        ability to *receive* DM's from another user.

        parameters
        -----------
        - sender = ''
        - message = ''

        if the user isn't blocked, then the message will be saved to self.dms
        with the senders name as the key, and the user will be notified.
        '''
        # is this sender blocked?
        if sender not in self.blocked:
            # store the message if we haven't gotten one from this user
            if sender not in self.dms.keys():
                self.dms[sender] = message
            # otherwise add to their list of messages
            else:
                self.dms[sender].extend(message)
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
                self.send(f'{user}: \n{self.dms[user]}'.encode('ascii'))
                return f'{user}: \n{self.dms[user]}'
            else:
                self.send(f'No messages from {user}!\n'.encode('ascii'))
                return f'No messages from {user}!'
        else:
            self.send('No messages!'.encode('ascii'))
            return 'No messages!'

    def read_all_dms(self):
        '''
        displays and returns a list of messages from other users as a string.
        '''
        if len(self.dms) > 0:
            dms = []
            for sender in self.dms:
                dms.append(f'{sender} : \n{self.dms[sender]}\n')
            dms_str = ' '.join(dms)
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
