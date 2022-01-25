#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A simple cmd2 application."""
import cmd2


class FirstApp(cmd2.Cmd):
    """A simple cmd2 application."""


if __name__ == '__main__':
    import sys
    c = FirstApp()
    sys.exit(c.cmdloop())
