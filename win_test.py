#!./bin/python3

import curses
from element import Element
from input_element import Input

from time import sleep

def main(screen):
    el = Element(screen)
    #inp = Input(screen)
    curses.doupdate()
    sleep(1)

curses.wrapper(main)
