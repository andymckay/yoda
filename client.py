from pull import get_pulls, PULLS
from jenkins import get_jenkins, REPOS

import irc.bot
import irc.strings

CONFIG = {
    'channel': ['#payments', '#amo'],
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

    def cmd_test(self):
        return ['Do. Or do not. There is no test.']

    def cmd_pulls(self):
        return get_pulls(PULLS)

    def cmd_jenkins(self):
        return get_jenkins(REPOS)

    def on_pubmsg(self, c, e):
        args = e.arguments[0].split(":", 1)
        if (len(args) > 1 and irc.strings.lower(args[0]) ==
            irc.strings.lower(self.connection.get_nickname())):
            command = self.get_command(args[1])
            if command:
                for response in command():
                    self.connection.privmsg(e.target, response)
            return

    def on_privmsg(self, c, e):
        command = self.get_command(e.arguments[0])
        if command:
            for response in command():
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
