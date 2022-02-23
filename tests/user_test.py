'''
user object testing
'''

from unittest import mock
from app.user import User

def test_instance():
    print('testing user instance...')
    mock_socket = mock.Mock()
    test_user = User(name = 'test_user', 
                     socket = mock_socket, 
                     curr_room = 'test_room')
    assert test_user.name == 'test_user'
    assert test_user.socket == mock_socket
    assert test_user.curr_room == 'test_room'
    assert test_user.curr_rooms == []
    assert test_user.blocked == []
    assert test_user.dms == {}
    print('...ok!')

def test_get_dm_from_unblocked_user():
    print('testing dm from unblocked user...')
    mock_socket = mock.Mock()
    test_user = User(name = 'test_user', 
                     socket = mock_socket, 
                     curr_room = 'test_room')
    sender = 'test_sender'
    message = 'this is a test message'

    test_user.get_dm(sender, message)
    assert sender not in test_user.blocked
    assert sender in test_user.dms.keys()
    assert test_user.dms[sender] == message
    print('...ok!')

def test_get_dm_from_blocked_user():
    print('testing dm from blocked user...')
    mock_socket = mock.Mock()
    test_user = User(name = 'test_user', 
                     socket = mock_socket, 
                     curr_room = 'test_room')
    sender = 'test_sender'
    message = 'this is a test message'

    test_user.block(sender)
    assert sender in test_user.blocked

    test_user.get_dm(sender, message)
    assert sender in test_user.blocked
    assert sender not in test_user.dms.keys()
    assert test_user.dms[sender] != message
    print('...ok!')

def test_read_dm():
    print('testing read dm...')
    mock_socket = mock.Mock()
    test_user = User(name = 'test_user', 
                     socket = mock_socket, 
                     curr_room = 'test_room')
    sender = 'test_sender'
    message = 'this is a test message'
    test_user.get_dm(sender, message)

    res = test_user.read_dm(sender)
    assert res == f'{sender}: \n{test_user.dms[sender]}'
    assert res != f'No messages from {sender}!'
    assert res != 'No messages!'
    print('...ok!')

def run_user_tests():
    print('\nStarting user tests...\n')
    test_instance()
    test_get_dm_from_unblocked_user()
    test_get_dm_from_blocked_user()
    test_read_dm()
    print("\n...done!")

if __name__ == '__main__':
    run_user_tests()