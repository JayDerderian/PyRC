'''
Jay Derderian
CS 594

a module for containing dictionaries about app information.
'''

APP_INFO = {
    "Name":  "PyChat",
    "Version": f'Version: {str(1.0)}',
    "Author": 'Author: Jay Derderian'
}


CLIENT_COMMANDS = {
    "Header" : "\n---------------------CLIENT COMMANDS-----------------------",
    "Space 1":   "                                                          ",
    "List":      "  /list :    Lists all rooms in the server                ",
    "Join":      "  /join :    Adds client to existing room, or creates     ",
    "Join2":     "             and joins room if it doesn't exist           ",
    "Join3":     "               ex: /join #dnd                             ",
    "Leave":     "  /leave :   Removes client from a room. Removes room     ",
    "Leave2":    "             from server when the last client leaves      ",
    "Leave3":    "               ex: /leave #dnd                            ",
    "Send":      "  /send :    Sends a message to the room client is in.    ",
    "Send2":     "             Can be sent to multiple rooms.               ",
    "Send3":     "               ex: /send #dnd Man, I love DND!            ",
    "Send4":     "               ex: /send #dnd #orcs Check out my sheet!   ",
    "Members":   "  /members : Lists all clients in a room.                 ",
    "Quit":      "  /quit :    Disconnects client from the server.          ",
    "Bottom":    "----------------------------------------------------------\n"
}