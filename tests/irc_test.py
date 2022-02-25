'''
IRC app testing
'''

from unittest import mock
from app.irc import IRC_App


def test_instantiation():
    print('testing app instantiation...')
    test_app = IRC_App()

    assert '#lobby' in test_app.rooms.keys()
    assert len(test_app.rooms) > 0
    assert test_app.users == {}
    print('...ok!')


def test_add_new_user():
    print('testing adding a new user...')
    test_app = IRC_App()
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
    test_app = IRC_App()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)
    test_app.add_user(test_user, test_socket)

    assert len(test_app.users) == 1
    assert test_user in test_app.users.keys()
    print('...ok!')


def test_remove_user():
    print('testing removing a user...')
    test_app = IRC_App()
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
    test_app = IRC_App()
    test_user = 'test_user'

    res = test_app.remove_user(test_user)

    assert res == f'{test_user} is not in the server!'
    print('...ok!')


def test_create_room():
    print('testing chatroom creation...')
    test_app = IRC_App()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)

    test_app.create_room('#test_room', test_user)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)
    print('...ok!')


def test_join_single_room():
    print('testing joining non-existant chatroom ...')
    test_app = IRC_App()
    test_user = 'test_user1'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)

    test_app.join_room('#test_room', test_user, test_socket)

    assert '#test_room' in test_app.rooms.keys()
    assert len(test_app.rooms) > 1
    assert test_app.rooms['#test_room'].has_user(test_user)
    print('...ok!')


def test_join_pre_existing_room():
    print("testing joining a pre-existing room...")
    test_app = IRC_App()
    test_user = 'test_user'
    test_socket = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user, test_socket)
    test_app.add_user(test_user2, test_socket2)
    test_app.create_room('#test_room', test_user)

    test_app.join_room('#test_room', test_user2, test_socket2)

    assert len(test_app.rooms['#test_room'].clients) == 2
    assert test_user in test_app.rooms['#test_room'].clients.keys()
    assert test_user2 in test_app.rooms['#test_room'].clients.keys()
    print('...ok!')


def test_join_multiple_rooms():
    ...


def test_leave_room():
    print("testing leaving a room...")
    test_app = IRC_App()
    test_user = 'test_user'
    test_socket = mock.Mock()

    test_app.add_user(test_user, test_socket)
    test_app.create_room('#test_room', test_user)

    test_app.leave_room('#test_room', test_user, test_socket)

    assert len(test_app.rooms['#test_room'].clients) == 0
    assert test_user in test_app.rooms['#lobby'].clients.keys()
    print('...ok!')


def test_get_all_users_in_app():
    print('testing getting list of all users in app...')
    test_app = IRC_App()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.join_room('#lobby', test_user1, test_socket1)
    test_app.join_room('#lobby', test_user2, test_socket2)

    user_list = test_app.get_all_users()
    user_keys = list(test_app.users.keys())

    assert user_list.split() == user_keys
    print('...ok!')


def test_get_single_room_users():
    print('testing getting user list from single room...')
    test_app = IRC_App()
    test_user1 = 'test_user1'
    test_socket1 = mock.Mock()
    test_user2 = 'test_user2'
    test_socket2 = mock.Mock()

    test_app.add_user(test_user1, test_socket1)
    test_app.add_user(test_user2, test_socket2)

    test_app.join_room('#lobby', test_user1, test_socket1)
    test_app.join_room('#lobby', test_user2, test_socket2)

    user_list = test_app.get_users('#lobby', test_socket1)
    user_keys = list(test_app.rooms['#lobby'].clients.keys())

    assert user_list.split() == user_keys
    assert user_list != '#lobby does not exist!'
    print('...ok!')


def test_parser_bad_input():
    print('testing parser with bad commands...')
    irc = IRC_App()
    test_user = 'test_user1'
    test_socket = mock.Mock()

    res = irc.message_parser('/whatev', test_user, test_socket)
    assert res == '/whatev is not a valid command!'

    res = irc.message_parser('/join', test_user, test_socket)
    assert res == "/join requires a #room_name argument.\nPlease enter: /join #roomname\n"

    res = irc.message_parser('/join room', test_user, test_socket)
    assert res == "/join requires a #room_name argument with '#' in front.\nPlease enter: /join #roomname\n"

    res = irc.message_parser('/message', test_user, test_socket)
    assert res == 'Error: /message requires a username argument. \nex: /message @<user_name> <message>'

    res = irc.message_parser('/message @user1 @user2', test_user, test_socket)
    assert res == 'Error: /message only takes one username argument. \nex: /message @<user_name> <message>'

    res = irc.message_parser('/dms user1', test_user, test_socket)
    assert res == 'Error: /message requires a "@" character to denote a user, ie @user_name'

    res = irc.message_parser('/whisper', test_user, test_socket)
    assert res == 'Error: No username argument found! \nuse syntax /whisper @<user_name> <message>'

    res = irc.message_parser('/whisper @user1 @user2', test_user, test_socket)
    assert res == 'Error: too many username arguments found! \nuse syntax /whisper @<user_name> <message>'

    print('...ok!')


def run_IRC_tests():
    print('\nStarting IRC application tests...\n')

    test_instantiation()
    test_add_new_user()
    test_add_user_that_already_exists()
    test_remove_user()
    test_remove_non_existant_user()
    test_create_room()
    test_join_single_room()
    test_join_pre_existing_room()
    # test_join_multiple_rooms()
    test_leave_room()
    test_get_single_room_users()
    test_get_all_users_in_app()
    test_parser_bad_input()
    
    print('\n...done!')

if __name__ == '__main__':
    run_IRC_tests()