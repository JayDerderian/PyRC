'''
Jay Derderian
CS 594

Application module - the core functionality of the IRC Chat program.

This handles tracking of clients and their associated sockets, sending
and recieving messages, message parsing, and other neccessary functionality.

There is also built-in debugging functionality using logs. 
Set DEBUG to true to turn on logging system.
'''

import socket
import logging

# Constants
DEBUG = False
if DEBUG:
    # start a log file for debugging
    logging.basicConfig(filename='IRC_App.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')

DEFAULT_ROOM_NAME = '#main'

# Broadcast a message to the server and to all clients in that room
def message_broadcast(room, name, socket, message):
    # Display message
    print(f'{room.name} : {name} > {message}\n')
    # Send the message to all clients except the one that sent the messaage
    for client_socket in room.client_sockets:
        if client_socket != socket:
            try:
                if DEBUG:
                    logging.info(f'app.message_broadcast() - sending: {room.name} : {name} > {message}')
                '''NOTE client will need to parse to use CLI!'''
                client_socket.send(f'{room.name} : {name} > {message}'.encode())
            except:
                print('IRC_APP ERROR : Failed to send message to client!')
                if DEBUG:
                    logging.debug(f'app.message_broadcast() - Failed to send message! Sender: {name}, Socket: {socket}')


# The container that has rooms, which have lists of clients
class IRC_Application:
    '''
    The main IRC application class. 
    '''
    def __init__(self):
        self.rooms = {}  # Create a dictionary of rooms. Key is the room_name, value is a ChatRoom() object.
        self.users = {}  # Dictionary of current users. Key is user_name, value is a tuple(current_room, user_socket)

    # Function to create a space-separated list of rooms
    def list_all_rooms(self):
        room_list = ""
        for room in self.rooms.values():
            room_list = room_list + room.name + ' '
        room_list = room_list + '\n'
        if DEBUG:
            logging.info(f'app.list_all_rooms() - generated room list: {room_list}')
        return room_list
    

    def show_current_room(self, user_name, room):
        '''
        display name of current room
        '''
        ...
    
    def show_connection_info(self, user_name):
        '''
        show current client's name, and socket info.
        '''
        ...

    # Check if the room name begins with '#', check if user is already in the room,
    # create the room if it does not exist, then join the room the user specified
    def join_room(self, room_to_join, sender_socket, sender_name):
        if room_to_join[0] != '#':
            if DEBUG:
                logging.info(f'app.join_room() - ERROR from {sender_name}, socket {sender_socket}: \nRoom name must begin with a #')
            sender_socket.send("Error: Room name must begin with a '#'\n".encode())
            return
        if room_to_join not in self.rooms:  # Assume that the room does not exist yet
            if DEBUG:
                logging.info(f'app.join_room() - created new room: {room_to_join}')
            self.create_room(room_to_join, sender_socket, sender_name)
        else:  # otherwise, go through the room members to make sure that the sender is not in it already
            for current_members in self.rooms[room_to_join].client_sockets:
                if sender_socket == current_members:
                    if DEBUG:
                        logging.debug(f'app.join_room - ERROR: {sender_name} attempted to join {room_to_join}, they were already there!')
                    sender_socket.send(f'Error: You are already in {room_to_join}\n'.encode())
                else:
                    # if we are here then the room exists and the sender is not in it.
                    self.rooms[room_to_join].add_new_client_to_chatroom(sender_name, sender_socket)
                    # keep track of where they are
                    self.users[sender_name] = (room_to_join, sender_socket)

    # Create a new Chatroom, add the room to the room list, and add the client to the chatroom
    # A room cannot exist without a client, so one must be supplied
    def create_room(self, room_to_join, sender_socket, sender_name):
        new_room = Chatroom(room_to_join)
        if DEBUG:
            logging.info(f'app.create_room() - New room {new_room.name} created')
        self.rooms[room_to_join] = new_room
        self.rooms[room_to_join].add_new_client_to_chatroom(sender_name, sender_socket)
        self.users[sender_name] = (room_to_join, sender_socket)

    # Check if the room exists, check if user is in the room,
    # remove user from room and delete room if it is empty
    def leave_room(self, room_to_leave, sender_socket, sender_name):
        if room_to_leave not in self.rooms:
            if DEBUG:
                logging.debug(f'app.leave_room() - ERROR: room {room_to_leave} does not exist!')
            sender_socket.send(f'Error: {room_to_leave} does not exist\n'.encode())
        elif sender_socket not in self.rooms[room_to_leave].client_sockets:
            if DEBUG:
                logging.debug(f'app.leave_room() - ERROR: {sender_name} attempted to leave non-existant room: {room_to_leave}')
            sender_socket.send(f'Error: You are not in {room_to_leave}\n'.encode())
        else:
            if DEBUG:
                logging.info(f'app.leave_room() - removing {sender_name} / {sender_socket} from {room_to_leave}')
            self.rooms[room_to_leave].remove_client_from_chatroom(sender_name, sender_socket)
            self.users[sender_name] = (DEFAULT_ROOM_NAME, sender_socket)
            if not self.rooms[room_to_leave].client_sockets:
                self.rooms.pop(room_to_leave)

    # Check if rooms exist, check if user is in rooms,
    # if room exists and user is in it then send message, otherwise skip
    def message_rooms(self, rooms_to_send, sender_socket, sender_name, message):
        for room in rooms_to_send:
            if room not in self.rooms:
                if DEBUG:
                    logging.debug(f'app.message_rooms()\n ERROR: {room} does not exist!')
                sender_socket.send(f'Error: {room} does not exist\n'.encode())
                continue
            if sender_socket not in self.rooms[room].client_sockets:
                if DEBUG:
                    logging.debug(f'app.message_rooms()\n ERROR: {sender_name} attempted to message {room}, which they are not in.')
                sender_socket.send(f'Error: You are not in {room}\n'.encode())
                continue
            message_broadcast(self.rooms[room], sender_name, sender_socket, message)

    def message_parse(self, sender_socket, sender_name, message):
        # Case where message is not a command:
        # The message is sent to the default channel
        '''
        NOTE: Will need to coordinate with the CLI instance on the Client application!
        '''
        if message[0] != '/':
            if DEBUG:
                logging.info(f'app.message_parse() - sending message from {sender_name} / {sender_socket} to all rooms')
                logging.info(f'app.message_parse() - {sender_name} : {message}')
            message_broadcast(self.rooms[DEFAULT_ROOM_NAME], sender_name, sender_socket, message)

        # Case where user wants to list all rooms:
        elif message.split()[0] == "/list" and len(message.split()) == 1:
            room_list = self.list_all_rooms()
            if DEBUG:
                logging.info(f'app.message_parse() - sending {sender_name} room list {room_list} to {sender_socket}')
            sender_socket.send(room_list.encode())

        # Case where user wants to join a room:
        elif message.split()[0] == "/join":
            if len(message.strip().split()) < 2:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /join argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send("/join requires a #room_name argument.\nPlease enter: /join #roomname\n".encode())
            else:
                self.join_room(message.split()[1], sender_socket, sender_name)

        # Case where user wants to leave a room:
        elif message.split()[0] == "/leave":
            if len(message.strip().split()) < 2:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /leave argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send("/leave requires a #roomname argument.\nPlease enter: /leave #roomname\n".encode())
            else:
                room_to_leave = message.strip().split()[1]
                if room_to_leave[0] != "#":
                    if DEBUG:
                        logging.info(f'app.message_parse() - improper /leave argument from {sender_name} / {sender_socket}')
                        logging.info(f'app.message_parse() - {message}')
                    sender_socket.send("/leave requires a #roomname argument to begin with '#'.\n".encode())
                else:
                    self.leave_room(room_to_leave, sender_socket, sender_name)

        # Case where user wants to send messages to rooms:
        # Parse the string for rooms and add rooms to a list
        # Pass the rest of the string along as the message
        elif message.split()[0] == "/send":
            rooms_to_send = []
            message_to_send = []
            convert_to_str = ""  # empty string to convert array into string
            # Add all the arguments beginning with # to a list of rooms
            if len(message) < 2:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /send argument from {sender_name} / {sender_socket}')
                sender_socket.send("/send requires a #roomname(s) argument(s).\nPlease enter: /send #roomname(s)\n".encode())
            else:
                for word in message.split():
                    if word[0] == '#':
                        rooms_to_send.append(word)
                    elif word[0] == '/':
                        continue
                    else:   # Assume the message is the string after the last room
                        message_to_send.append(word)
                if rooms_to_send.count == 0:
                    if DEBUG:
                        logging.info(f'app.message_parse() - ')
                    sender_socket.send("/send at least one #roomname(s) argument(s).\nPlease enter: /send #roomname(s)\n".encode())
                else:
                    convert_to_str = ' '.join([str(word) for word in message_to_send])
                    convert_to_str = convert_to_str + '\n'
                    if DEBUG:
                        logging.info(f'app.message_parse() - sending message from {sender_name} / {sender_socket}')
                        logging.info(f'app.message_parse() - {convert_to_str}')
                    self.message_rooms(rooms_to_send, sender_socket, sender_name, convert_to_str)


        # list all members in a room
        elif message.split()[0] == "/members":
            if len(message.split()) != 2:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /members argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send("/members requires a single #roomname argument.\nPlease enter: /members #roomname\n".encode())
            elif message.split()[1][0] != '#':
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /members argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send("Room names must begin with a #\n".encode())
            elif message.split()[1] not in self.rooms:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /members argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')                
                sender_socket.send("That room does not exist.\n".encode())
            else:
                room_name = message.split()[1]
                client_list = self.rooms[room_name].list_clients_in_room()
                new_message = ' '.join(client_list)
                new_message = new_message + '\n'
                if DEBUG:
                    logging.info(f'app.message_parse() - sending message from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send(new_message.encode())
            
        # exit app
        elif message.split()[0] == "/quit":
            if len(message.split()) != 1:
                if DEBUG:
                    logging.info(f'app.message_parse() - improper /quit argument from {sender_name} / {sender_socket}')
                    logging.info(f'app.message_parse() - {message}')
                sender_socket.send("/quit takes no arguments\n".encode())
            else:
                sender_socket.shutdown(socket.SHUT_WR)

        # elif message.split()[0] == "/pm":


class Chatroom:
    '''
    NOTE. create a self.text_color field to display all text for this
          chatroom in a specific color.
    '''
    # Give a Chatroom a name and list of client's sockets in this room 
    def __init__(self, room_name, text_color=None):
        self.name = room_name
        self.text_color = text_color
        self.client_sockets = []
        self.clients = {}       # A dictionary of clients with sockets as the key and username as the value

    # Adds a new client to a chatroom and notifies clients in that room
    def add_new_client_to_chatroom(self, client_name, new_socket):
        self.client_sockets.append(new_socket)
        self.clients[new_socket] = client_name
        message = f"{client_name} has joined the room.\n"
        if DEBUG:
            logging.info(f'app.add_new_client_to_chatroom - {client_name} / {new_socket} has joined the room')
        message_broadcast(self, client_name, new_socket, message)

    # Removes an existing client from a chatroom and notifies the clients in that room
    def remove_client_from_chatroom(self, client_name, client_socket):
        self.client_sockets.remove(client_socket)
        self.clients.pop(client_socket)
        message = f"{client_name} has left the room.\n"
        if DEBUG:
            logging.info(f'app.add_new_client_to_chatroom - {client_name} / {client_socket} has left the room')
        message_broadcast(self, client_name, client_socket, message)

    def list_clients_in_room(self):
        return list(self.client_list.values())
