import os
from sys import stdin, stdout

try:
    from termios import *
except ImportError:
    from TERMIOS import *


class Term:
    """ Linux terminal management.

        getch   - get one char at a time
        size    - return height, width of the terminal
    """
    def __init__(self):
        self.fd = stdin.fileno()
        self.new_term, self.old_term = tcgetattr(self.fd), tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~ICANON & ~ECHO)

    def normal(self):
        """Set 'normal' terminal settings."""
        tcsetattr(self.fd, TCSAFLUSH, self.old_term)

    def cline(self):
        """Clear line."""
        stdout.write('\r' + ' '*self.size()[1])
        stdout.flush()

    def curses(self):
        """Set 'curses' terminal settings. (noecho, something else?)"""
        tcsetattr(self.fd, TCSAFLUSH, self.new_term)

    def getch(self, prompt=None):
        """ Get one character at a time.

            NOTE: if the user suspends (^Z) running program, then brings it back to foreground,
            you have to instantiate Term class again.  Otherwise getch() won't work. Even after
            that, the user has to hit 'enter' once before he can enter commands.
        """
        if prompt:
            stdout.write(prompt)
            stdout.flush()
        self.curses()
        c = os.read(self.fd, 1)

        # handle terminal escape code
        if c == '\x1b':
            c = os.read(self.fd, 2)
        self.normal()
        return c

    def size(self):
        """Return terminal size as tuple (height, width)."""
        import struct, fcntl
        h, w = struct.unpack("hhhh", fcntl.ioctl(0, TIOCGWINSZ, "\000"*8))[0:2]
        if not h:
            h, w = 24, 80
        return h, w
