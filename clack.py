#!./bin/python

from slacker import Slacker
from sys import argv, stdin, stdout, stderr
from multiprocessing import Pool
from time import sleep
import os
import select
import curses

#setup default variables 
variables = dict()
variables['prompt'] = "clack>"
prompt_start = (0, len(variables['prompt']))
variables["channel"] = '#general'
variables["username"] = None
variables["logfile"] = "clack.log"

#check args
#if len(argv) > 1:
#    username = argv[1]
#else:
#    username = "clackbot"

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

    def event_handler(event):
        return

    def add_msg(scr, user, msg):
        scr.scroll()
        scr.addstr(scr.getmaxyx()[0] - 1, 0, user + ':')
        scr.addstr(scr.getmaxyx()[0] - 1, len(user + ':'), msg)
        scr.noutrefresh()

    def send_dm(user, msg):
        return False

    slack = Slacker(variables["apikey"])

    #init messaging 
    response = slack.rtm.start()
    variables['teamname'] = response.body['team']['name']
    userlist = response.body['users']
    chanlist = response.body['channels']
    grouplist = response.body['groups']
    botlist = response.body['bots']

    #draw initial windows
    screen_height = screen.getmaxyx()[0]
    screen_width = screen.getmaxyx()[1]

    if curses.has_colors():
        curses.init_color(0,0,250,400)

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

    loc = input_panel.getmaxyx()

    prompt_text = variables['prompt']
    text_input = input_panel.derwin(loc[0] - 2,loc[1] - 2, 1,1)
    text_input.addstr(0,0,prompt_text)
    text_input.noutrefresh()

    output_panel = screen.derwin(left_panel.getmaxyx()[0] - input_panel.getmaxyx()[0], \
            screen_width - left_panel.getmaxyx()[1] - 1, 1, left_panel.getmaxyx()[1] + 1)
    output_panel.border(0)
    output_panel.noutrefresh()

    loc = output_panel.getmaxyx()
    text_output = output_panel.derwin(loc[0] - 2, loc[1] - 2, 1,1)
    text_output.scrollok(True)
    text_output.noutrefresh()

    curses.doupdate()

    running = True
    while running:
        chanlist = refresh_channels(channel_panel)
        userlist = refresh_users(user_panel)

        curses.echo()
        msg = text_input.getstr(prompt_start[0],prompt_start[1]).rstrip();
        curses.cbreak()

        text_input.clear()
        text_input.addstr(0,0,prompt_text)
        text_input.move(prompt_start[0],prompt_start[1])
        text_input.refresh()

        if len(msg):
            if msg[0] == '/':
                cmd = msg[1:].split(' ')
                if cmd[0] == "quit":
                    running = False
                elif cmd[0] == "dm":
                    send_dm(cmd[1],cmd[2:])
                elif cmd[0] == "sw":
                    win = cmd[1]
                    if [0] == '#':
                        variables["channel"] = channel
                    else:
                        user = win

            else:
                slack.chat.post_message(variables["channel"], msg)
                add_msg(text_output, variables["username"], msg)
                text_output.refresh()


    #log.close()
    return 0

curses.wrapper(clack)

