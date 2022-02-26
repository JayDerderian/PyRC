'''
runs all unit tests
'''

from tests.user_test import run_user_tests
from tests.chatroom_test import run_chatroom_tests
from tests.irc_test import run_IRC_tests


def run_tests():
    print('\n***Starting integration tests***')
    run_user_tests()
    run_chatroom_tests()
    run_IRC_tests()
    print('\n**All tests passed!**\n')


if __name__ == '__main__':
    run_tests()