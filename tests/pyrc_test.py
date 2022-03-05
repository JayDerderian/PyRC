'''
PyRC app testing
'''

from unittest import mock
from app.pyrc import PyRC


def test_instantiation():
    print('testing app instantiation...')
    test_app = PyRC()

    assert '#lobby' in test_app.rooms.keys()
    assert len(test_app.rooms) > 0
    assert test_app.users == {}
    print('...ok!')


def test_add_new_user():
    print('testing adding a new user...')
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)

    assert test_user in test_app.users.keys()
    assert len(test_app.users) > 0
    assert '#lobby' in test_app.rooms.keys()
    assert len(test_app.rooms) > 0
    assert test_user in test_app.rooms['#lobby'].clients.keys()
    print('...ok!')


def test_add_user_that_already_exists():
    print('testing adding a pre-existing user...')
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)
    test_app.add_user(test_user, test_socket)

    assert len(test_app.users) == 1
    assert test_user in test_app.users.keys()
    print('...ok!')


def test_remove_user():
    print('testing removing a user...')
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)
    res = test_app.remove_user(test_user)

    assert test_user not in test_app.users.keys()
    assert len(test_app.users) == 0
    assert res != f'{test_user} is not in the server!'
    print('...ok!')


def test_remove_non_existant_user():
    print('testing removing a non-existant user...')
    test_app = PyRC()
    test_user = 'test_user'

    res = test_app.remove_user(test_user)

    assert res == f'{test_user} is not in the server!'
    print('...ok!')


def test_create_room():
    print('testing chatroom creation...')
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)

    # create non-existant room
    test_app.create_room('#test_room', test_user)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)

    # remove room and try with parser
    del test_app.rooms['#test_room']

    msg = '/create #test_room'
    test_app.message_parser(msg, test_user, test_socket)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)
    print('...ok!')

def test_join_single_room():
    print('testing joining non-existant chatroom ...')
    test_app = PyRC()
    test_user = 'test_user1'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)

    test_app.join_room('#test_room', test_user)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)
    assert test_user in test_app.rooms['#test_room'].clients.keys()

    # try with parser
    del test_app.rooms['#test_room']

    msg = '/join #test_room'
    test_app.message_parser(msg, test_user, test_socket)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)
    assert test_user in test_app.rooms['#test_room'].clients.keys()

    print('...ok!')


def test_join_pre_existing_room():
    print("testing joining a pre-existing room...")
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user, test_socket)
    test_app.add_user(test_user2, test_socket2)
    test_app.create_room('#test_room', test_user)

    test_app.join_room('#test_room', test_user2)

    assert len(test_app.rooms['#test_room'].clients) == 2
    assert test_user in test_app.rooms['#test_room'].clients.keys()
    assert test_user2 in test_app.rooms['#test_room'].clients.keys()

    # try with parser
    del test_app.rooms['#test_room']
    test_app.create_room('#test_room', test_user)
    test_app.join_room('#test_room', test_user2)

    msg = '/join #test_room'
    test_app.message_parser(msg, test_user, test_socket)

    assert len(test_app.rooms['#test_room'].clients) == 2
    assert test_user in test_app.rooms['#test_room'].clients.keys()
    assert test_user2 in test_app.rooms['#test_room'].clients.keys()

    print('...ok!')


def test_join_multiple_rooms():
    print("testing joining multiple rooms...")
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_app.add_user(test_user, test_socket)

    rooms_to_join = ['#test_room1', '#test_room2', '#test_room3']
    for room in rooms_to_join:
        test_app.join_room(room, test_user)
    # #lobby + 3 new rooms
    assert len(test_app.rooms) == 4

    # confirm the user has been added to these rooms
    for room in test_app.rooms:
        assert test_app.rooms[room].has_user(test_user)
        assert test_user in test_app.rooms[room].clients.keys()

    # try with parser
    for room in rooms_to_join:
        del test_app.rooms[room]
    # make sure we only have the #lobby    
    assert len(test_app.rooms) == 1    

    msg = '/join #test_room1 #test_room2 #test_room3'
    test_app.message_parser(msg, test_user, test_socket)

    assert len(test_app.rooms) == 4

    for room in test_app.rooms:
        assert test_app.rooms[room].has_user(test_user)
        assert test_user in test_app.rooms[room].clients.keys()

    print('...ok!')


def test_join_multiple_rooms_with_parser():
    print("testing joining multiple rooms using parser...")
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_app.add_user(test_user, test_socket)  

    msg = '/join #room1 #room2 #room3'
    test_app.message_parser(msg, test_user, test_socket)

    assert '#room1' in test_app.rooms.keys()
    assert '#room2' in test_app.rooms.keys()
    assert '#room3' in test_app.rooms.keys()
    assert test_user in test_app.rooms['#room1'].clients.keys()
    assert test_user in test_app.rooms['#room2'].clients.keys()
    assert test_user in test_app.rooms['#room3'].clients.keys()
    print("...ok!")


def test_leave_room():
    print("testing leaving a room...")
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_app.add_user(test_user, test_socket)

    test_app.create_room('#test_room', test_user)

    test_app.leave_room('#test_room', test_user)

    assert len(test_app.rooms['#test_room'].clients) == 0
    assert test_user in test_app.rooms['#lobby'].clients.keys()

    # try with parser
    del test_app.rooms['#test_room']
    test_app.create_room('#test_room', test_user)

    msg = '/leave #test_room'
    test_app.message_parser(msg, test_user, test_socket)

    assert len(test_app.rooms['#test_room'].clients) == 0
    assert test_user in test_app.rooms['#lobby'].clients.keys()

    print('...ok!')


def test_leaving_all_rooms():
    print("testing leaving all active rooms...")
    test_app = PyRC()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_app.add_user(test_user, test_socket)

    test_room_names = ['Room A', 'Room B', 'Room C', 'Room D', 'Room E']
    # add five rooms
    for add in range(5):
        test_app.create_room(test_room_names[add], test_user)
    # make sure they're there
    for name in range(5):
        assert test_app.rooms[test_room_names[name]].has_user(test_user)
    
    # remove from all 
    test_app.leave_all(test_user)

    # make sure they've been removed from all
    for name in range(5):
        assert len(test_app.rooms[test_room_names[name]].clients) == 0
    # make sure users' active room list has been updated accordingly
    for name in range(5):
        assert test_room_names[name] not in test_app.users[test_user].curr_rooms

    # make sure #lobby is still in curr_room list
    assert '#lobby' in test_app.users[test_user].curr_rooms
    # make sure user is still in #lobby client dict
    assert test_user in test_app.rooms['#lobby'].clients.keys()

    # try with parser
    for room in test_room_names:
        del test_app.rooms[room]
    
    # add five rooms
    for add in range(5):
        test_app.create_room(test_room_names[add], test_user)
    # make sure they're there
    for name in range(5):
        assert test_app.rooms[test_room_names[name]].has_user(test_user)

    msg = '/leave all'
    test_app.message_parser(msg, test_user, test_socket)
    
    # make sure they've been removed from all
    for name in range(5):
        assert len(test_app.rooms[test_room_names[name]].clients) == 0
    # make sure users' active room list has been updated accordingly
    for name in range(5):
        assert test_room_names[name] not in test_app.users[test_user].curr_rooms

    # make sure #lobby is still in curr_room list
    assert '#lobby' in test_app.users[test_user].curr_rooms
    # make sure user is still in #lobby client dict
    assert test_user in test_app.rooms['#lobby'].clients.keys()

    print("...ok!")


def test_get_all_users_in_app():
    print('testing getting list of all users in app...')
    test_app = PyRC()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.join_room('#lobby', test_user1)
    test_app.join_room('#lobby', test_user2)

    user_list = test_app.get_all_users()
    user_keys = list(test_app.users.keys())

    assert user_list.split() == user_keys
  
    print('...ok!')


def test_get_single_room_users():
    print('testing getting user list from single room...')
    test_app = PyRC()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.join_room('#lobby', test_user1)
    test_app.join_room('#lobby', test_user2)

    user_list = test_app.get_users('#lobby', test_socket1)
    user_keys = list(test_app.rooms['#lobby'].clients.keys())

    assert user_list.split() == user_keys
    assert user_list != '#lobby does not exist!'

    print('...ok!')


def test_block_user():
    print('testing blocking a user...')
    test_app = PyRC()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.block(test_user1, test_user2)
    test_app.send_dm(test_user2, 'test message', test_user1)

    assert test_user2 in test_app.users[test_user1].blocked
    assert test_user2 not in test_app.users[test_user1].dms.keys()

    print('...ok!')


def test_unblock_user():
    print('testing unblocking a user...')
    test_app = PyRC()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.block(test_user1, test_user2)
    assert test_user2 in test_app.users[test_user1].blocked

    test_app.unblock(test_user1, test_user2)
    assert test_user2 not in test_app.users[test_user1].blocked

    print('...ok!')


def test_broadcast():
    print('testing broadcast...')
    test_app = PyRC()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_app.add_user(test_user1, test_socket1)

    msg = '/broadcast #room1 : hello room 1! / #room2 : hello room 2! / #room3 : hello room 3! /'

    room_names = ['#room1', '#room2', '#room3']
    messages = ['hello room 1!', 'hello room 2!', 'hello room 3!']

    res = test_app.message_parser(msg, test_user1, test_socket1)
    assert res != 'Error: must include at least one room name and messsage! \nex: /broadcast #room_name : <message> /'
    assert res != 'Error: must include a message! \nex: /broadcast #room_name : <message> /'
    assert res != 'Error: unequal amounts of rooms and messages!'
    assert type(res) == dict
    assert 'Rooms' in res.keys()
    assert 'Messages' in res.keys()
    assert len(res['Rooms']) == len(res['Messages'])
    assert room_names == res['Rooms']
    assert messages == res['Messages']

    print("...ok!")


def test_parser_with_bad_input():
    print('testing parser with bad commands...')
    irc = PyRC()
    test_user = 'test_user1'
    test_socket = mock.Mock()

    res = irc.message_parser('/whatev', test_user, test_socket)
    assert res == '/whatev is not a valid command!'

    res = irc.message_parser('/join', test_user, test_socket)
    assert res == "/join requires a #room_name argument.\nPlease enter: /join #roomname\n"

    res = irc.message_parser('/join room', test_user, test_socket)
    assert res == "/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n"

    res = irc.message_parser('/join #room room', test_user, test_socket)
    assert res == 'Error: incorrect syntax! all room names must start with a "#"'

    res = irc.message_parser('/leave', test_user, test_socket)
    assert res == "/leave requires a #room_name argument.\nPlease enter: /leave #roomname\n"

    res = irc.message_parser('/leave room', test_user, test_socket)
    assert res == "/leave requires a #roomname argument to begin with '#'.\n"

    res = irc.message_parser('/create', test_user, test_socket)
    assert res == 'Error: must include a room name argument separated with a space \nex: /create #room_name'

    res = irc.message_parser('/create room', test_user, test_socket)
    assert res == 'Error: must include a "#" when denoting a room name! \nex: /create #room_name'

    res = irc.message_parser('/message', test_user, test_socket)
    assert res == 'Error: /message requires a username argument. \nex: /message @<user_name> <message>'

    res = irc.message_parser('/message @user1 @user2', test_user, test_socket)
    assert res == 'Error: /message only takes one username argument. \nex: /message @<user_name> <message>'

    res = irc.message_parser('/broadcast', test_user, test_socket)
    assert res == 'Error: must include at least one room name and messsage! \nex: /broadcast #room_name : <message> /'

    res = irc.message_parser('/broadcast #room', test_user, test_socket)
    assert res == 'Error: must include a message! \nex: /broadcast #room_name : <message> /'

    res = irc.message_parser('/broadcast #room hello there', test_user, test_socket)
    assert res == 'Error: all messages must end with a "/" to denote ending. \nex: /broadcast #room_name : <message> /'

    res = irc.message_parser('/dms user1', test_user, test_socket)
    assert res == 'Error: /message requires a "@" character to denote a user, ie @user_name'

    res = irc.message_parser('/block', test_user, test_socket)
    assert res == 'Error: /block requires at least one user_name argument!'

    res = irc.message_parser('/unblock', test_user, test_socket)
    assert res == 'Error: /unblock requires at least one user_name argument!'

    res = irc.message_parser('/whisper', test_user, test_socket)
    assert res == 'Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'

    res = irc.message_parser('/whisper @user1 @user2', test_user, test_socket)
    assert res == 'Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'

    print('...ok!')


def run_PyRC_tests():
    print('\nStarting IRC application tests...\n')

    test_instantiation()
    test_add_new_user()
    test_add_user_that_already_exists()
    test_remove_user()
    test_remove_non_existant_user()
    test_create_room()
    test_join_single_room()
    test_join_pre_existing_room()
    test_join_multiple_rooms()
    test_join_multiple_rooms_with_parser()
    test_leave_room()
    test_leaving_all_rooms()
    test_get_single_room_users()
    test_get_all_users_in_app()
    test_block_user()
    test_unblock_user()
    test_broadcast()
    test_parser_with_bad_input()
    
    print('\n...done!')

if __name__ == '__main__':
    run_PyRC_tests()