import asyncio
import importlib
import os
import sys
import threading
import time
from StorageClasses import context

class Main(object):
    def __init__(self, client):
        self.in_messages = []
        self.out_messages = []
        self.connected = False
        self.client = client

        self.pugs = {}
        self.pickingpug = {}
        self.picking = False
        self.pickturn = None

    def set_config(self, config):
        self.raw_config = config.raw_config
        self.commands = config.command_config

    def message_handler(self, message, edit=False):
        if message.content.lstrip().startswith(self.raw_config['Main']['command char']): #removes leading spaces and checks that the message begins with the command character
            self.message_parser(message, edit)

    def message_parser(self, message, edit):
        content = [a.split() for a in message.content.split(self.raw_config['Main']['command char'])[1:]]
        for item in content:
            self.in_messages.append([item, message])

    def command_handler(self):
        for content, message in self.in_messages:
            self.in_messages.pop(0)
            if message.channel.id in self.commands.command_tree and content[0] in self.commands[message.channel.id]:
                command = self.commands[message.channel.id][content[0]]
                print('Processed message: ', message.content, message.channel)
                accepted_roles = set([role.name for role in message.author.roles]) & set(command.roles)
                if accepted_roles:
                    ctx = context.Context()
                    ctx.accepted_roles = accepted_roles
                    ctx.message_content = content
                    command(self, message, ctx)
                    break

    def message_printer(self, message, channel, header='', msg_break=''):
        if channel == 'hub':
            channel = self.hub_channel
        self.out_messages.append([channel, message, header, msg_break])
