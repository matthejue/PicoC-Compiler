#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A simple cmd2 application."""
import cmd2


class FirstApp(cmd2.Cmd):
    """A simple cmd2 application."""
    def __init__(self):
        super().__init__()

        cmd2.Cmd.prompt = "PicoC>"
        cmd2.Cmd.continuation_prompt = ">"

        # Make maxrepeats settable at runtime
        self.maxrepeats = 3
        self.add_settable(
            cmd2.Settable('maxrepeats', int,
                          'max repetitions for speak command', self))

    speak_parser = cmd2.Cmd2ArgumentParser()
    speak_parser.add_argument('-p',
                              '--piglatin',
                              action='store_true',
                              help='atinLay')
    speak_parser.add_argument('-s',
                              '--shout',
                              action='store_true',
                              help='N00B EMULATION MODE')
    speak_parser.add_argument('-r',
                              '--repeat',
                              type=int,
                              help='output [n] times')
    speak_parser.add_argument('words', nargs='+', help='words to say')

    @cmd2.with_argparser(speak_parser)
    def do_speak(self, args):
        """Repeats what you tell me to."""
        words = []
        for word in args.words:
            if args.piglatin:
                word = '%s%say' % (word[1:], word[0])
            if args.shout:
                word = word.upper()
            words.append(word)
        repetitions = args.repeat or 1
        for _ in range(min(repetitions, self.maxrepeats)):
            # .poutput handles newlines, and accommodates output redirection too
            self.poutput(' '.join(words))


if __name__ == '__main__':
    import sys
    c = FirstApp()
    sys.exit(c.cmdloop())
