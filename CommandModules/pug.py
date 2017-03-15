import random
from command import command

@command(aliases=['c'], description='Creates a pug **(Usage: .create <pug name> <player amount>)**')
def create(self, message, ctx):
    if not ctx.message_content[-1].isdigit():
        self.message_printer('Please specify a player amount at the end of your command', message.channel)
        return

    if int(ctx.message_content[-1]) <= 1:
        self.message_printer('Please use a valid player amount (bigger or equal to 2)', message.channel)
        return

    self.pugs.update({' '.join(ctx.message_content[1:-1]):[int(ctx.message_content[-1])+1, message.author]})
    self.message_printer('You have created a new pug!', message.channel)

@command(aliases=['ls'], description='Lists current pugs')
def list(self, message, ctx):
    output = ['**__Current Pugs__**']
    for pug_name, players in self.pugs.items():
       output.append('**{}** with `{}` ({}/{})'.format(pug_name, ','.join([player.name for player in players[1:]]), len(players)-1, players[0]-1))

    self.message_printer('\n'.join(output), message.channel)

@command(aliases=['j'], description='Joins a pug')
def join(self, message, ctx):
    pug = ' '.join(ctx.message_content[1:])

    if pug not in self.pugs:
        self.message_printer('That pug does not exist', message.channel)
        return

    if message.author in self.pugs[pug]:
        self.message_printer('You are already in that pug', message.channel)
        return

    self.pugs[pug].append(message.author)
    self.message_printer(message.author.name + ' has been added to the pug', message.channel)
    
    if len(self.pugs[pug]) == self.pugs[pug][0]:
        self.picking = True
        available_players = self.pugs[pug][1:]
        redcapt = available_players.pop(random.randint(0, len(available_players)-1))
        bluecapt = available_players.pop(random.randint(0, len(available_players)-1))
        self.pickturn = 'redcapt'
        self.picking_pug = {'redcapt':(redcapt, 'redteam', 'bluecapt'), 'bluecapt':(bluecapt, 'blueteam', 'redcapt'), 'redteam':[redcapt], 'blueteam':[bluecapt], 'avail':available_players, 'all':available_players}
        del(self.pugs[pug])

        output = []
        output.append('Pug full')
        output.append('Congratulations {0} and {1} you captain the red and blue team respectively, {0} begins picking'.format(redcapt.mention, bluecapt.mention))

        self.message_printer('\n'.join(output), message.channel)
        return

@command(aliases=['p'], description='Picks someone to be on your team in a pug **(Usage: .pick <player number>)**')
def pick(self, message, ctx):
    if not self.picking:
        self.message_printer('There are currently no full pugs', message.channel)
        return

    if self.picking_pug[self.pickturn][0] != message.author:
        self.message_printer('You can\'t pick right now', message.channel)
        return

    if len(ctx.message_content) != 2 or not ctx.message_content[1].isdigit():
        self.message_printer('Please use valid input', message.channel)
        return

    index = int(ctx.message_content[1])
    if index > len(self.picking_pug['all']) or self.picking_pug['all'][index] not in self.picking_pug['avail']:
        self.message_printer('That player is not available', message.channel)
        return

    pp = self.picking_pug

    pp[pp[self.pickturn][1]].append(pp['avail'].pop(pp['avail'].index(pp['all'][index])))
    self.message_printer('You have successfully picked {}'.format(pp['all'][index].name), message.channel)

    self.pickturn = pp[self.pickturn][2]
    if len(pp['avail']) == 1:
        pp[pp[self.pickturn][1]].append(pp['avail'][0])
        output = ['Teams have been picked:']
        output.append('Red team: '+ ','.join([player.name for player in pp['redteam']]))
        output.append('Blue team: '+ ','.join([player.name for player in pp['blueteam']]))

        self.message_printer('\n'.join(output), message.channel)
        self.picking = False
    else:
        self.message_printer('{}, it is your turn to pick'.format(pp[self.pickturn][0].mention), message.channel)
        

@command(aliases=['picks'], description='Show who is available to be picked')
def showpicks(self, message, ctx):
    if not self.picking:
        self.message_printer('There are currently no full pugs', message.channel)
        return

    output = ['**Current picking session:**']
    output.append('Available players: '+ ', '.join(['{}:{}'.format(self.picking_pug['all'].index(player), player.name) for player in self.picking_pug['avail']]))
    output.append('Red team: '+ ','.join([player.name for player in self.picking_pug['redteam']]))
    output.append('Blue team: '+ ','.join([player.name for player in self.picking_pug['blueteam']]))
    self.message_printer('\n'.join(output), message.channel)

@command(aliases=['l'], description='Leave a pug, **(Usage: .leave <pug name>)**')
def leave(self, message, ctx):
    chosen_pug = ' '.join(ctx.message_content[1:])
    print(self.pugs, chosen_pug)
    if chosen_pug in self.pugs:
        if message.author in self.pugs[chosen_pug]:
            self.pugs[chosen_pug].remove(message.author)
            self.pugs[chosen_pug][0] = self.pugs[chosen_pug][0]-1
            self.message_printer('**{0}** has left **{1}**, players left: **{2}**'.format(message.author.name, chosen_pug, len(self.pugs[chosen_pug])-1), message.channel)

            if len(self.pugs[chosen_pug]) == 1:
                self.message_printer('No one left in **{0}**, pug terminated'.format(chosen_pug), message.channel)
                del(self.pugs[chosen_pug])

        else:
            self.message_printer('You are not in that pug', message.channel)
    else:
        self.message_printer('That pug does not exist', message.channel)

@command(aliases=['lva'], description='Leave all pugs you are a part of')
def leaveall(self, message, ctx):
    output1 = []
    output2 = []
    removelist = []
    for pug in self.pugs:
        if message.author in self.pugs[pug]:
            self.pugs[pug].remove(message.author)
            output1.append('**{0}** has left **{1}**, players left: **{2}**'.format(message.author.name, pug, len(self.pugs[pug])-1))

            if len(self.pugs[pug]) == 1:
                removelist.append(pug)
                output2.append('No one left in **{0}**, pug terminated'.format(pug))

    for pug in removelist:
        del(self.pugs[pug])

    if output1:
        self.message_printer('\n'.join(output1), message.channel)

        if output2:
            self.message_printer('\n'.join(output2), message.channel)

    else:
        self.message_printer('You are not in any pugs', message.channel)
