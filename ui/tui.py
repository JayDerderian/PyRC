'''
Jay Derderian
CS 594

This module handles the TUI for this application. 
Randomly assigns a font color and background color for a chatroom.
'''

import os
import sys
from random import choice

from art import (
    tprint, text2art, aprint, art_dic, font_list,
    FONT_NAMES, decor, decor_dic, randart,
)

import colorama
from colorama import (
    Fore, Back, Style
)
colorama.init(autoreset=True)

class TUI:
    '''
    import and instantiate this class to use foreground and background
    colors in the terminal. 

    made using ANSI Escape Sequence color constants and the termcolor module

    NOTE: MAY NOT WORK IN ALL TERMINALS. 
    
    Depends on whether the OS has ANSI enabled.
    Use supports_colors() before instantiating TUI()!
    '''
    def __init__(self, debug=False):
        
        self.debug = debug

        self.rooms = {}   # key is room name, value is a list with fg color and bg color
        self.names = {}   # key is user name, value is assigned color

        ######################
        # ANSI COLOR STRINGS #
        ######################

        # text functionality
        self.alts = {
            'reset': '\033[0m',
            'bold': '\033[01m',
            'disable': '\033[02m',
            'underline': '\033[04m',
            'reverse': '\033[07m',
            'strikethrough': '\033[09m',
            'invisible': '\033[08m'
        }
    
        # foreground colors
        self.fg = {
            'black': '\033[30m',
            'red':  '\033[31m',
            'green': '\033[32m',
            'orange': '\033[33m',
            'blue': '\033[34m',
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'lightgrey': '\033[37m',
            'darkgrey': '\033[90m',
            'lightred': '\033[91m',
            'lightgreen': '\033[92m',
            'yellow': '\033[93m',
            'lightblue': '\033[94m',
            'pink': '\033[95m',
            'lightcyan': '\033[96m'
        }

        # background colors
        self.bg = {
            'black': '\033[40m',
            'red': '\033[41m',
            'green': '\033[42m',
            'orange': '\033[43m',
            'blue': '\033[44m',
            'purple': '\033[45m',
            'cyan': '\033[46m',
            'lightgrey': '\033[47m'
        }

        ####################
        # COLORAMA STRINGS #
        ####################

        # foreground colors
        self.colorfg = {
            'black': Fore.BLACK,
            'blue': Fore.BLUE,
            'cyan': Fore.CYAN,
            'green': Fore.GREEN,
            'magenta': Fore.MAGENTA, 
            'red': Fore.RED,
            'white': Fore.WHITE,
            'yellow': Fore.YELLOW,
            'light black': Fore.LIGHTBLACK_EX,
            'light blue': Fore.LIGHTBLUE_EX,
            'light cyan': Fore.LIGHTCYAN_EX,
            'light green': Fore.LIGHTGREEN_EX,
            'light magenta': Fore.LIGHTMAGENTA_EX,
            'light red': Fore.LIGHTRED_EX,
            'light white': Fore.LIGHTWHITE_EX,
            'light yellow': Fore.LIGHTYELLOW_EX,
        }

        self.colorbg = {
            'black': Back.BLACK,
            'blue': Back.BLUE,
            'cyan': Back.CYAN,
            'green': Back.GREEN,
            'magenta': Back.MAGENTA,
            'red': Back.RED,
            'white': Back.WHITE,
            'yellow': Back.YELLOW,
            'light black': Back.LIGHTBLACK_EX,
            'light blue': Back.LIGHTBLUE_EX,
            'light cyan': Back.LIGHTCYAN_EX,
            'light green': Back.LIGHTGREEN_EX,
            'light magenta': Back.LIGHTMAGENTA_EX,
            'light red': Back.LIGHTRED_EX,
            'light white': Back.LIGHTWHITE_EX,
            'light yellow': Back.LIGHTYELLOW_EX,
        }

    ## TESTER ###

    def test(self):
        f = choice(FONT_NAMES) 
        print('\n', text2art(text='HELLO', font=f))
        print(f'\nFONT: {f}\n')
        
    ############## FANCY STUFF ###############

    def rainbow_word(self, word):
        '''
        prints a word out letter by letter each with an individual color
        '''
        letters = word.split()

    ############### CLIENT UI ################

    def client_menu(self, menu:list[str]):
        '''
        displays a menu utilizing a list of strings representing 
        each line in the menu.
        '''
        for line in menu:
            print(text2art(menu[line], font='tiny2'))

    def assign_colors(self, message):
        '''
        assign a text color and background color for a chatroom
        '''
        # break message apart, parse for #room name and randomly
        # choose colors for each. 
        if message == '#lobby':
            self.rooms[message] = [self.colorfg['light blue'], None]
        else:
            message = message.split()
            for word in message:
                # actually add room names and not just room joining acknowledgements
                if word[0] == '#' and word[-1] != '!' and word not in self.rooms.keys():
                    # [0] == text color 
                    # [1] == background color for message text
                    self.rooms[word] = [choice(list(self.colorfg.values())), 
                                        choice(list(self.colorbg.values()))] 
    
    def get_colors(self, room):
        '''
        retrieve associated fg/bg colors with this room. assign one if it doesn't
        have any already
        '''
        return self.rooms[room] if room in self.rooms.keys() else self.assign_colors(room)


    def display(self, message):
        '''
        take a message from the server, add a color to the room name,
        the display message

        if message.split()[n] == ':'
            use list slice to get everything AFTER the index of ':' and before a '#'
        '''
        # match room names with their foreground colors 
        new_rooms = []
        orig_rooms = []
        message_ = message.split()

        # add ANSI colors to room name strings
        for word in message_:
            if word[0] == '#' and word in self.rooms.keys():
                room_name_with_color = f'\n{self.rooms[word][0]}{word}{Fore.RESET}'
                new_rooms.append(room_name_with_color)
                orig_rooms.append(word)

        # replace original instances with newly colorized room 
        for room in range(len(orig_rooms)):
            ind = message_.index(orig_rooms[room])
            message_[ind] = new_rooms[room]

        # display final message
        print(" ".join(message_))


    def shut_down_message(self, message):
        '''
        'SERVER OFFLINE! Closing connection...'
        '''
        print(f'{Fore.RED}{Back.WHITE}{message}{Style.RESET_ALL}')
    
    def connected_message(self, message):
        '''
        'Connected!'
        '''
        print(f'{Fore.GREEN}{message}{Style.RESET_ALL}')
 
    def error_messages(self, errors):
        '''
        Display an error message, or list of messages
        '''
        if type(errors) == str:
            print(f'{Fore.RED} ERROR: {errors}{Style.RESET_ALL}')
        elif type(errors) == list:
            print(f'{Fore.RED} ERROR')
            for e in range(len(errors)):
                print(f'{Fore.RED}{e} : {errors[e]}{Style.RESET_ALL}')
        else:
            raise TypeError('errors must be a single str or list[str]! type is:', type(errors))

# App info display. Not contingent on a computers ability to support colors.
def app_info(info:dict):
    '''
    displays app info
    (author, version # (with date))
    '''
    print(text2art(info["Name"], font='tarty2'))
    print(art_dic.art_dic["kirby dance"], '\n')
    print(text2art(info["Version"], font='tiny2'))
    print(text2art(info["Author"], font='tiny2'), '\n')


def supports_color():
    '''
    Returns True if the running system's terminal supports color using 
    ANSI escape codes in Windows. 

    Technique from:
        https://stackoverflow.com/questions/7445658/how-to-detect-if-the-console-does-support-ansi-escape-codes-in-python
        https://github.com/django/django/blob/main/django/core/management/color.py
    '''
    def vt_codes_enabled_in_windows_registry():
        """
        Check the Windows Registry to see if VT code handling has been enabled
        by default, see https://superuser.com/a/1300251/447564.
        """
        try:
            # winreg is only available on Windows.
            import winreg
        except ImportError:
            return False
        else:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
            try:
                reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
            except FileNotFoundError:
                return False
            else:
                return reg_key_value == 1

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    return is_a_tty and (
        sys.platform != "win32"
        or "ANSICON" in os.environ
        or
        # Windows Terminal supports VT codes.
        "WT_SESSION" in os.environ
        or
        # Microsoft Visual Studio Code's built-in terminal supports colors.
        os.environ.get("TERM_PROGRAM") == "vscode"
        or vt_codes_enabled_in_windows_registry()
    )