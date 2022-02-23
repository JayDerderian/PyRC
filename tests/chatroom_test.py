'''
chatroom object testing
'''


from unittest import mock
from app.chatroom import Chatroom


def test_instance():
    print('testing chatroom instance...')
    test_room = Chatroom(room_name='test_room')
    assert test_room.name == 'test_room'
    assert test_room.clients == {}
    print('...ok!')

def test_add_new_client():
    print('testing add new client...')
    test_room = Chatroom(room_name='test_room')
    test_user_object = mock.Mock()
    test_user_object.name = 'test_user'
    test_room.add_new_client_to_room(test_user_object)
    assert len(test_room.clients) > 0
    assert test_user_object.name in test_room.clients.keys()
    assert test_room.clients[test_user_object.name] == test_user_object
    print('...ok!')

def test_remove_client():
    print('testing remove client....')
    # first make sure client was added
    test_room = Chatroom(room_name='test_room')
    test_user_object = mock.Mock()
    test_user_object.name = 'test_user'
    test_room.add_new_client_to_room(test_user_object)
    assert len(test_room.clients) > 0
    assert test_user_object.name in test_room.clients.keys()
    assert test_room.clients[test_user_object.name] == test_user_object

    # then make sure it was removed!
    test_room.remove_client_from_room(test_user_object.name)
    assert len(test_room.clients) == 0
    print('...ok!')

def run_chatroom_tests():
    print('\nStarting chatroom tests...\n')
    test_instance()
    test_add_new_client()
    test_remove_client() 
    print("\n...done!")

if __name__ == '__main__':
    run_chatroom_tests()