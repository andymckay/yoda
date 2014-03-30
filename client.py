from pull import get_pulls, PULLS
from jenkins import get_jenkins, REPOS

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
            print "joining,", channel
            c.join(channel)

    def get_command(self, arg):
        return getattr(self, 'cmd_{0}'.format(arg.strip().lower()), None)

    def cmd_test(self, person=None):
        if person:
            return ['Do. Or do not. There is no test, %s.'
                    % person.capitalize()]
        return ['Do. Or do not. There is no test.']

    def cmd_pulls(self, person=None):
        out = []
        if person:
            out.append('pull requests for {0}...'.format(person))
        out.extend(get_pulls(PULLS, person=person))
        return out

    def cmd_jenkins(self, **kw):
        return get_jenkins(REPOS)

    def get_person(self, command, e):
        start = e.arguments[0].find(command)
        person = e.arguments[0][start+len(command)+1:] or None
        return person

    def on_pubmsg(self, c, e):
        args = e.arguments[0].split(":", 1)
        if (len(args) > 1 and irc.strings.lower(args[0]) ==
            irc.strings.lower(self.connection.get_nickname())):
            arg = args[1].strip().split(' ')[0]
            command = self.get_command(arg)
            if command:
                for response in command(person=self.get_person(arg, e)):
                    self.connection.privmsg(e.target, response)
            return

    def on_privmsg(self, c, e):
        args = e.arguments[0].strip().split(' ')[0]
        command = self.get_command(args)
        if command:
            for response in command(person=e.source.nick):
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
