'''
runs all unit tests
'''

from user_test import run_user_tests
from chatroom_test import run_chatroom_tests
from irc_test import run_IRC_tests


def run_tests():
    print('\nStarting unit tests...')
    run_user_tests()
    run_chatroom_tests()
    run_IRC_tests()
    print('\n**All tests passed!**')


if __name__ == '__main__':
    run_tests()