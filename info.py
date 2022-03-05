'''
Jay Derderian
CS 594

a module for containing dictionaries about app information.
'''

APP_INFO = {
    "Name":  "PyRC",
    "Version": f'Version: {str(1.0)}',
    "Author": 'Author: Jay Derderian'
}


CLIENT_COMMANDS = {
    "Header" :   "\n------------------------CLIENT COMMANDS-----------------------",
    "Space 1":   "                                                              ",
    "Chat":      "  (No command) <message>: Send message to all your rooms      ",
    "Chat2":     "                          #lobby is the default room.         ",
    "Blank":     "                                                              ",
    "Rooms":     "  /rooms :   List all currently active rooms.                 ",
    "My Rooms":  "  /myrooms : List all your active rooms.                      ",
    "Users":     "  /users :   List all users in the application                ",
    "Blank2":    "                                                              ",
    "Join":      "  /join :    Adds client to existing room, or creates         ",
    "Join2":     "             and joins room if it doesn't exist               ",
    "Join3":     "               ex: /join #dnd -or- #join #coding #dnd ...     ",
    "Create":    "  /create :  Creates a new chatroom if it doesn't exist.      ",
    "Create2":   "               ex: /create #room                              ",
    "Leave":     "  /leave :   Leave a room.                                    ",
    "Leave3":    "               ex: /leave #dnd                                ",
    "Blank3":    "                                                              ",
    "Broadcast": "  /broadcast : Send distinct messages to multiple rooms.      ",
    "Broadcast2":"   ex: /broadcast #room1 : <message1> / #room2 : <message2> / ",
    "Blank4":    "                                                              ",
    "Message":   "  /message : Send a direct message (DM) to another user.      ",
    "Message2":  "             ex: /message @user_name <message>                ",
    "Blank5":    "                                                              ",
    "DMs":       "  /dms :     Get your direct messages. Add a username to get  ",
    "DMs2":      "             messages from a specific user.                   ",
    "DMs3":      "                ex: /dms -or - /dms @user_name                ",
    "Blank6":    "                                                              ",
    "Whisper":   "  /whisper : Send a private message to another user           ",
    "Whisper2":  "                ex: /whisper @user_name <message>             ",
    "Blank7":    "                                                              ",
    "Block":     "  /block :   Block a user.                                    ",
    "Block2":    "                ex: /block @user_name                         ",
    "Unblock":   "  /unblock : Unblock a user                                   ",
    "Unblock2":  "                ex: /unblock @user_name                       ",
    "Blank8":    "                                                              ",
    "Help":      "  /help:     Display available commands                       ",        
    "Quit":      "  /quit :    Disconnects client from the server.              ",
    "Bottom":    "--------------------------------------------------------------\n"
}