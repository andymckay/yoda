import queue
from jenkins import get_jenkins, REPOS
from pull import get_pulls, PULLS

import irc.bot
import irc.strings


CONFIG = {
    'channel': ['#payments', '#marketplace'],
    'nickname': 'yoda',
    'server': 'irc.mozilla.org',
    'port': 6667
}


class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, channels, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)],
                                            nickname, nickname)
        self.init_channels = channels

    def _process_line(self, *args, **kw):
        super(Bot, self)._process_line(*args, **kw)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel in self.init_channels:
            c.join(channel)

    def get_command(self, arg):
        arg = (arg.replace('+', '_plus').replace('-', '_minus')
               .replace('?', '_list'))
        return getattr(self, 'cmd_{0}'.format(arg.strip().lower()), None)

    def cmd_test(self, person=None, **kw):
        if person:
            return ['Do. Or do not. There is no test, %s.'
                    % person.capitalize()]
        return ['Do. Or do not. There is no test.']

    def cmd_pulls(self, person=None, **kw):
        out = []
        if person:
            out.append('pull requests for {0}...'.format(person))
        out.extend(get_pulls(PULLS, person=person))
        return out

    def cmd_jenkins(self, **kw):
        return get_jenkins(REPOS)

    def cmd_q_plus(self, person=None, **kw):
        out = []
        if not person:
            out.append('Know which person to add to queue I do not.')
            return out

        queue.add(person)
        out.append('In the queue: %s' % ', '.join(queue.listing()))
        return out

    def cmd_q_minus(self, person=None, **kw):
        out = []
        if not person:
            out.append('Know which person to remove from queue I do not.')
            return out

        queue.remove(person)
        out.append('In the queue: %s' % ', '.join(queue.listing()))
        return out

    def cmd_q_minus_minus(self, **kw):
        queue.reset()
        return []

    def cmd_q_list(self, **kw):
        return ['In the queue: %s' % ', '.join(queue.listing())]

    def get_person(self, command, e):
        start = e.arguments[0].find(command)
        person = e.arguments[0][start+len(command)+1:] or None
        return person

    def sanitize(self, text):
        return text.strip().split(' ')[0]

    def on_pubmsg(self, c, e):
        args = e.arguments[0].split(":", 1)
        if (len(args) > 1 and irc.strings.lower(args[0]) ==
            irc.strings.lower(self.connection.get_nickname())):
            arg = self.sanitize(args[1])
            command = self.get_command(arg)
            if command:
                for response in command(person=self.get_person(arg, e),
                                        event=e):
                    self.connection.privmsg(e.target, response)
            else:
                self.connection.privmsg(e.target,
                    'Know this command: %s, I do not.' % args[1])
            return

    def on_privmsg(self, c, e):
        args = e.arguments[0].strip().split(' ')[0]
        command = self.get_command(args)
        if command:
            for response in command(person=e.source.nick,
                                    event=e):
                self.connection.privmsg(e.source.nick, response)
        return


def main():
    bot = Bot(CONFIG['channel'],
              CONFIG['nickname'],
              CONFIG['server'],
              CONFIG['port'])
    bot.start()

if __name__ == "__main__":
    main()
