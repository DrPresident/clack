#!./bin/python
from slackclient import SlackClient
from sys import argv, stdin, stdout, stderr
from time import sleep
from threading import Lock, Thread
from async import Async
import os
import select
import curses

#setup default variables 
variables = dict()
variables['prompt'] = "clack>"
prompt_start = (0, len(variables['prompt']))
variables["channel"] = 'general'
variables["username"] = "Clack"
variables["logfile"] = "run.log"
async = Async()

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

    def refresh_header(scr, channel, num_users):
        scr.clear()

        if channel:
            scr.addstr(0, 2, '#' + channel)
        if num_users > -1:
            user_start = scr.getmaxyx()[1] - len("users: " + str(num_users)) - 10
            log.write("user_start: " + str(user_start) + '\n')
            scr.addstr(0, user_start, "users: " + str(num_users))

        scr.noutrefresh()

    def refresh_users(scr, offset = 0):
        response = slack.api_call("users.list")
        userlist = response['members']

        scr.addstr(1, 1, "Users")
        for u in range(offset, len(userlist)):
            userlist[u] = (userlist[u]['name'],userlist[u]['id'])
            scr.addstr(u + 2, 1, "  " + userlist[u][0])
        scr.noutrefresh()

        return userlist

    def refresh_channels(scr, offset = 0):
        response = slack.api_call("channels.list")
        chanlist = response['channels']

        scr.addstr(1, 1, "Channels")
        for c in range(offset, len(chanlist)):
            chanlist[c] = (chanlist[c]['name'],chanlist[c]['id'])
            scr.addstr(c + 2, 1, "  #" + chanlist[c][0])
            if chanlist[c][0] == variables['channel']:
                variables['chanid'] = chanlist[c][1]

        scr.noutrefresh()

        return chanlist

    def setup_chan(scr, chan):
        if chan[0] != '#':
            chan = '#' + chan
        response = slack.api_call("channels.info",channel=chan)
        log.write("channels.info: " + chan + "\n" + str(response))

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

                    scr.noutrefresh()

    def add_msg(scr, user, msg):
        scr.scroll()
        scr.addstr(scr.getmaxyx()[0] - 1, 0, user + ':')
        scr.addstr(scr.getmaxyx()[0] - 1, len(user + ':'), msg)
        scr.refresh()

    def send_dm(user, msg=None):
        return False

    def event_handler(scr):

        chanlist = refresh_channels(channel_panel)
        userlist = refresh_users(user_panel)
        refresh_header(text_header, variables['channel'], len(userlist))
        prechan = variables['channel']

        while running:

            if variables['channel'] != prechan:
                refresh_header(text_header, variables['channel'], len(userlist))
                prechan = variables['channel']

            events = slack.rtm_read()
            for event in events:
                if event['type'] == "hello":
                    log.write("hello!\n")

                elif event['type'] == "message":
                    if event['channel'] == variables['chanid']:
                        if "user" in event.keys():
                            key = "user"
                        else:
                            key = "username"

                        for u in userlist:
                            if u[1] == event[key]:
                                add_msg(scr, u[0], event['text'])
                                break
                        break
                elif "channel" in event['type']:
                    chanlist = refresh_channels(channel_panel)
                else:
                    log.write("unhandled event: " + event['type'] + '\n')

    slack = SlackClient(variables["apikey"])
    log = open(variables["logfile"], "w")

    #draw initial windows
    screen_height = screen.getmaxyx()[0]
    screen_width = screen.getmaxyx()[1]

    if curses.has_colors() and curses.can_change_color():
        curses.init_color(0,0,300,500)

    left_panel = screen.derwin(screen_height, screen_width / 5, 0,0)
    left_panel.border(0)
    left_panel.noutrefresh()

    channel_panel = left_panel.derwin(left_panel.getmaxyx()[0] / 2, left_panel.getmaxyx()[1], 0,0) 
    channel_panel.noutrefresh()


    user_panel = left_panel.derwin((left_panel.getmaxyx()[0] / 2 + left_panel.getmaxyx()[0] % 2),\
            left_panel.getmaxyx()[1], left_panel.getmaxyx()[0] / 2, 0)
    user_panel.noutrefresh()

    input_panel = screen.derwin(4, screen_width - left_panel.getmaxyx()[1] - 1, 
            screen_height - 4, left_panel.getmaxyx()[1] + 1)
    input_panel.border(0)
    input_panel.noutrefresh()

    loc = input_panel.getmaxyx()

    prompt_text = variables['prompt']
    text_input = input_panel.derwin(loc[0] - 2,loc[1] - 2, 1,1)
    text_input.addstr(0,0,prompt_text)
    text_input.noutrefresh()

    header_panel = screen.derwin(3,
            screen_width - left_panel.getmaxyx()[1] - 1,
            0, left_panel.getmaxyx()[1] + 1)
    header_panel.border(0)
    header_panel.noutrefresh()

    text_header = header_panel.derwin(1,header_panel.getmaxyx()[1] - 2, 1, 1)
    text_header.noutrefresh()

    output_panel = screen.derwin(screen_height - header_panel.getmaxyx()[0] - input_panel.getmaxyx()[0], 
            screen_width - left_panel.getmaxyx()[1] - 1, 
            header_panel.getmaxyx()[0], left_panel.getmaxyx()[1] + 1)
    output_panel.border(0)
    output_panel.noutrefresh()

    loc = output_panel.getmaxyx()

    text_output = output_panel.derwin(loc[0] - 2, loc[1] - 2, 1,1)
    text_output.scrollok(True)
    text_output.noutrefresh()

    setup_chan(text_output, variables["channel"])

    response = slack.api_call("rtm.start")
    log.write("rtm.start\n" + str(response) + '\n')

    if slack.rtm_connect():
        async.start_daemon(event_handler, [text_output])
        variables['teamname'] = response['team']['name']
        variables['username'] = response['self']['name']
        grouplist = response['groups']
        botlist = response['bots']
    else:
        log.write("Error: could not connect to rtm")

    curses.doupdate()

    running = True
    while running:

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

                elif cmd[0] == "p" or cmd[0] == "print":
                    add_msg(text_output, "print " + cmd[1], cmd[1:])

                #dm user
                elif cmd[0] == "dm" and len(cmd) >= 2:
                    if len(cmd) >= 3:
                        send_dm(cmd[1],cmd[2:])
                    else:
                        variables["channel"] = "user:" + cmd[1]

                #switch channel|user
                elif cmd[0] == "sw":
                    win = cmd[1]
                    if [0] == '#':
                        variables["channel"] = channel
                    else:
                        user = win

                #join channel
                elif cmd[0] == "join" and len(cmd) >= 2:
                    if cmd[1][0] != '#':
                        cmd[1] = '#' + cmd[1]
                    response = slack.api_call("channels.join", name=cmd[1])

                    if(response['ok'] == True):
                        variables["channel"] = response['channel']['name']
                        variables["chanid"] = response['channel']['id']

                        #getting channel history
                        hresponse = slack.api_call("channels.history", channel = response['channel']['id'])
                        if hresponse['ok'] == True:
                            msgs = hresponse['messages']

                #leave channel
                elif cmd[0] == "leave":
                    continue
                #kick user from channel
                elif cmd[0] == "kick":
                    continue
                #change topic of channel
                elif cmd[0] == "topic":
                    continue

            else:
                response = slack.api_call("chat.postMessage", 
                        channel=variables["channel"], 
                        text=msg,
                        as_user=True)

    log.close()
    return 0

curses.wrapper(clack)
