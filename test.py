'''
runs all unit tests
'''

from time import time

from tests.user_test import run_user_tests
from tests.chatroom_test import run_chatroom_tests
from tests.pyrc_test import run_PyRC_tests


def run_tests():
    start_time = time()

    print('\n***Starting integration tests***')

    run_user_tests()
    run_chatroom_tests()
    run_PyRC_tests()
    
    print('\n**All tests passed!**\n')

    end_time = time()-start_time
    print("\nruntime:", end_time, "seconds\n")


if __name__ == '__main__':
    run_tests()