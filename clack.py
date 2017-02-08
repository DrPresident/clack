#!./bin/python

from slackclient import SlackClient
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
variables["username"] = "Clack"
variables["logfile"] = "run.log"

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
        response = slack.api_call("users.list")
        userlist = response['members']

        scr.addstr(1, 1, "Users")
        for u in range(offset, len(userlist)):
            scr.addstr(u + 2, 1, "  " + userlist[u]['name'])
        scr.noutrefresh()

        return userlist

    def refresh_channels(scr, offset = 0):
        response = slack.api_call("channels.list")
        chanlist = response['channels']

        scr.addstr(1, 1, "Channels")
        for c in range(offset,len(chanlist)):
            scr.addstr(c + 2, 1, "  #" + chanlist[c]['name'])
        scr.noutrefresh()
        return chanlist

    def event_handler(event):
        return

    def setup_chan(scr, chan):
        if chan[0] != '#':
            chan = '#' + chan
        response = slack.api_call("channels.info",channel=chan)
        log.write("channels.join: " + chan + "\n" + str(response))

        if(response['ok'] == True):
            hresponse = slack.api_call("channels.history",
                    channel=response['channel']['name'])
            log.write("channels.history: " + chan + "\n" + str(hresponse))
            if hresponse['ok'] == True:
                variables["channel"] = response['channel']['name']
                msgs = hresponse['messages']
                log.write(msgs + '\n')

                for msg in msgs:
                    scr.scroll()
                    scr.addstr(scr.getmaxyx()[0] - 1, 0, msg['user'] + ':')
                    scr.addstr(scr.getmaxyx()[0] - 1, len(msg['user']) + 1, 
                            msg['text'])
                    #add_msg(text_output, msg['user'], msg['text'])

                scr.noutrefresh()
        
    def add_msg(scr, user, msg):
        scr.scroll()
        scr.addstr(scr.getmaxyx()[0] - 1, 0, user + ':')
        scr.addstr(scr.getmaxyx()[0] - 1, len(user + ':'), msg)
        scr.noutrefresh()

    def send_dm(user, msg=None):
        return False

    def rtm_update(scr, userlist):
        events = slack.rtm_read()
        for event in events:
            log.write(str(event) + '\n')
            if event['type'] == "hello":
                continue
            elif event['type'] == "message":
                for u in userlist:
                    if u['id'] == event['user']:
                        add_msg(scr, u['name'], event['text'])
                        break
            else:
                log.write("unhandled event: " + event['type'] + '\n')

    slack = SlackClient(variables["apikey"])
    log = open(variables["logfile"], "w")

    #init messaging 

    response = slack.api_call("rtm.start")
    if not slack.rtm_connect():
        log.write("Error: could not connect to rtm")
        exit(1)

    variables['teamname'] = response['team']['name']
    variables['username'] = response['self']['name']
    log.write(response['self']['name'])
    userlist = response['users']
    chanlist = response['channels']
    grouplist = response['groups']
    botlist = response['bots']

    #draw initial windows
    screen_height = screen.getmaxyx()[0]
    screen_width = screen.getmaxyx()[1]

    if curses.has_colors() and curses.can_change_color():
        curses.init_color(0,0,300,500)

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

    setup_chan(text_output, variables["channel"])

    curses.doupdate()

    running = True
    while running:
        chanlist = refresh_channels(channel_panel)
        userlist = refresh_users(user_panel)

        rtm_update(text_output, userlist)
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

                #variable assignment
                if "=" in cmd and len(cmd) == 3:
                    variables[cmd[0]] = cmd[2]
                #commands
                elif cmd[0] == "quit":
                    running = False

                elif cmd[0] == "dm" and len(cmd) >= 2:
                    if len(cmd) >= 3:
                        send_dm(cmd[1],cmd[2:])
                    else:
                        variables["channel"] = "user:" + cmd[1]

                elif cmd[0] == "sw":
                    win = cmd[1]
                    if [0] == '#':
                        variables["channel"] = channel
                    else:
                        user = win

                elif cmd[0] == "join" and len(cmd) >= 2:
                    if cmd[1][0] != '#':
                        cmd[1] = '#' + cmd[1]
                    response = slack.api_call("channels.join", name=variables["username"])

                    if(response['ok'] == True):
                        hresponse = slack.api_call("channels.history", 
                                channel=response['channel']['name'])
                        if hresponse['ok'] == True:
                            variables["channel"] = response['channel']['name']
                            msgs = hresponse['messages']

                elif cmd[0] == "leave":
                    continue
                elif cmd[0] == "kick":
                    continue
                elif cmd[0] == "topic":
                    continue

            else:
                slack.api_call("chat.postMessage", 
                        channel=variables["channel"], 
                        text=msg)
                add_msg(text_output, variables["username"], msg)

    #sock.close()
    log.close()

    return 0

curses.wrapper(clack)

