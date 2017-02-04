#!./bin/python

from slacker import Slacker

slack = Slacker('xoxp-136383196064-137780673271-137781258231-\
        2a20cd639e916cbcac5baa166dba1fdb')
slack.chat.post_message('#general','clack')

response = slack.users.list()
users = response.body['members']

