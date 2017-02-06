#!./bin/python

from slacker import Slacker
from sys import argv, stdin, stdout, stderr
import os
import select
import curses

variables = dict()

#setup curses
def curses_setup():
    scr = curses.initscr()
    scr.keypad(1)
    curses.noecho()
    curses.cbreak()
    return scr

#revert curses settings
def curses_reset(scr):
    scr.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


#check cmd args
if len(argv) > 1:
    username = argv[1]
else:
    username = "clackbot"

try:
    config = open(os.path.join(os.path.expanduser('~'), ".clackrc"))
    for line in config:
        line = line.split('=') 
        var = line[0]
        val = line[1]
        variables[var.lower()] = val

    config.close()

except Exception as e:
    print e

#setup default variables if not in clackrc
if not variables.has_key("apikey"):
    stderr.write("no apikey given\n")
    exit(1)
if not variables.has_key("prompt"):
    variables['prompt'] = "clack>"
if not variables.has_key("start_channel"):
    variables["start_channel"] = '#general'
if not variables.has_key("username"):
    variables["username"] = "user!"

try:
    print variables['apikey']
    slack = Slacker(variables["apikey"])

    cscreen = curses_setup()

    response = slack.users.list()
    users = response.body['members']
    response = slack.channels.list()
    channels = response.body['channels']

    slack.chat.post_message(varibales["start_channel"],'this is a message from clack', username=variables["username"])

    chanlist = list()
    for chan in channels:
        chanlist.append(chan['name'])
        print chan['name']

    print channels[0]['name']

finally:
    curses_reset(cscreen)
