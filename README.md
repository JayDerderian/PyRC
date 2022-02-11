# Table of Contents
* [Introduction](#Introduction)
* [Technologies](#Technologies)
* [Installation](#Installation)
* [Client Commands](#ClientCommands)
* [License](#License)

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
```/list```: Lists all rooms in the server.  
```/join```: Adds client to an existing room, or creates and joins a room if the room does not exist.  
```
/join #coding
```
```/leave```: Removes a client from a room. Removes the room from the server when the last client leaves.  
```
/leave #coding
```
```/send```: Sends a message to a room the client has joined. Can send to multiple rooms.  
```
/send #coding Boy I sure love Python!
/send #coding #python Look at this IRC app I made!
```
```/members```: Lists all clients in the room the user is currently in.  
```/quit```: Disconnects the client from the server.  

# License

