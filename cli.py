'''
Jay Derderian
CS 594

This module handles the cli for this application. 
'''
from sys import stdout, stdin
from termcolor import colored as color


class CLI:
    '''
    import and instantiate this class to use foreground and background
    colors in the terminal while using the IRC application. 

    to display the username with black text on a light grey background
       print(CLI.bg.lightgrey, username, colors.fg.black) 

    made using ANSI Escape Sequence color constants and the termcolor module
    more info -> https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    '''
    def __init__(self):
        self.reset = '\033[0m'
        self.bold = '\033[01m'
        self.disable = '\033[02m'
        self.underline = '\033[04m'
        self.reverse = '\033[07m'
        self.strikethrough = '\033[09m'
        self.invisible = '\033[08m'
    
    # foreground colors
    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green ='\033[32m'
        orange ='\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    # background colors
    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'

    # input prompt
    def input_prompt(user):
        print(color(f'{user} > ', 'blue'))