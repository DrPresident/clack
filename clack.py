#!./bin/python

from slacker import Slacker
from sys import argv, stdin, stdout, stderr
import os
import select
import curses
from time import sleep

#setup default variables 
variables = dict()
variables['prompt'] = "clack>"
variables["start_channel"] = '#general'
variables["username"] = "user!"

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
        val = val.rstrip()
        variables[var.lower()] = val

    config.close()

except Exception as e:
    print e

if not variables.has_key("apikey"):
    stderr.write("no apikey given\n")
    exit(1)

def clack(screen):

    def refresh_users(scr, offset = 0):
        response = slack.users.list()
        users = response.body['members']

        userlist = list()
        l = 0
        for user in users:
            userlist.append(user['name'])
            l += 1
        scr.addstr(1, 1, "Users")
        for u in range(offset, l):
            scr.addstr(u + 3, 1, "  " + userlist[u])
        scr.noutrefresh()
        return userlist

    def refresh_channels(scr, offset = 0):

        response = slack.channels.list()
        channels = response.body['channels']

        chanlist = list()
        l = 0
        for chan in channels:
            chanlist.append(chan['name'])
            l += 1
        scr.addstr(1, 1, "Channels")
        for c in range(offset,l):
            scr.addstr(c + 3, 1, "  #" + chanlist[c])
        scr.noutrefresh()
        return chanlist

    def update_msgs(scr, msg):

        cap = scr.getmaxyx()[0] - 1
        for m in range(1, cap):
            scr.addstr(m, 1, msgs[m])
        scr.noutrefresh()

    def send_dm(user, msg):
        return False

    slack = Slacker(variables["apikey"])
    running = True

    screen_height = screen.getmaxyx()[0]
    screen_width = screen.getmaxyx()[1]

    #draw initial windows
    left_panel = screen.derwin(screen_height - 1, screen_width / 5, 1,1)
    left_panel.border(0)
    left_panel.noutrefresh()

    channel_panel = left_panel.derwin(left_panel.getmaxyx()[0] / 2, left_panel.getmaxyx()[1], 0,0) 
    channel_panel.noutrefresh()

    user_panel = left_panel.derwin((left_panel.getmaxyx()[0] / 2 + left_panel.getmaxyx()[0] % 2),\
            left_panel.getmaxyx()[1], left_panel.getmaxyx()[0] / 2, 0)
    user_panel.noutrefresh()

    input_panel = screen.derwin(4, screen_width - left_panel.getmaxyx()[1] - 1, \
            screen_height - 4, left_panel.getmaxyx()[1] + 1) 
    input_panel.border(0)
    input_panel.noutrefresh()

    output_win = screen.derwin(left_panel.getmaxyx()[0] - input_panel.getmaxyx()[0], \
            screen_width - left_panel.getmaxyx()[1] - 1, 1, left_panel.getmaxyx()[1] + 1)
    output_win.border(0)
    output_win.noutrefresh()

    curses.doupdate()

    while running:
        chanlist = refresh_channels(channel_panel)
        userlist = refresh_users(user_panel)

        curses.echo()
        msg = input_panel.getstr(1,1).rstrip();
        curses.cbreak()

        input_panel.clear()
        input_panel.border(0)
        input_panel.refresh()

        if msg[0] == '/':
            if msg[1:5] == "quit":
                running = False
            elif msg[1:3] == "dm":
        else:
            output_win.addstr(1,1,variables["username"] + ">" + msg)
            output_win.refresh()

        input_panel.move(1,1)

    return 0

curses.wrapper(clack)
