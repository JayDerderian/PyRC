# Table of Contents
* [Introduction](#Introduction)
* [Technologies](#Technologies)
* [Installation](#Installation)
* [Client Commands](#ClientCommands)

# Introduction
This project implements a client and server for an Internet Relay Chat (IRC) application. 
The server is able to relay text between clients using websockets. Clients are able to make chatrooms and send messages to rooms for other clients to see. Users also have a range of text commands to utilize the application in different ways. 

# Technologies
This was written in Python primarily using the socket module, and other select packages. See requirements.txt for full dependency list.

# Installation
Make sure that you have Python 3.6 or later installed. The following commands will install the project and run the server.

```
git clone https://github.com/<tbd>

cd pychat
python Server.py
```

You will need additional windows to run client applications.

```
python Client.py
```

# Client Commands
```(No command) <message>```: Send a message to all the rooms you're active in.  
```/rooms```: List all active rooms in the server.                               
```/myrooms```: List all the rooms you're active in.                                 
```/join```: Adds client to an existing room, or creates and joins a room if the room does not exist. User can join multiple rooms at once. 
```
/join #coding -or- /join #room1 #room2 #room3
```
```/create```: Create a new room if it doesn't already exist.                               
```
/create #room
```
```/leave```: Removes a client from a room. Removes the room from the server when the last client leaves. Use 'all' argument to leave all active rooms except the #lobby. 
```
/leave #coding -or- /leave all
```
```/users```: List all user in the server.                               
````/broadcast```: Send *distinct* messages to *multiple* rooms, regardless if you're in those rooms.
```
/broadcast #room1 : <message1> / #room2 : <message2 / 
```
```/mute```: Mute output from selected rooms. 
```
/mute #room1 #room2
```
```/unmute```: Unmute output from selected rooms
```
/unmute #room1 #room2 -or- /unmute all
```
```/message```: Send a direct message to another user. 
```
/message @user_name <message>
```
```/dms```: Retrieve your direct messages. Add a user name argument to get messages from a specified user.
```
/dms -or- /dms @user_name
```
```/whisper```: Directly message another user in real-time, regardless if they're in the same room as you.
```
/whisper @user_name <message>
```
```/block```: Block a user.
```
/block @user_name
```
```/unblock```: Unblock a user.
```
/unblock @user_name
```
```/clear```: Clear terminal window.                      
```/help```: Display available commands.                                                            
```/quit```: Disconnects the client from the server.     
