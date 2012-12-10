Words
=====

In the Words game, the goal is to reveal all of words by guessing letters one at a time. Each
time a letter is guessed correctly, a random letter from a different word will also be revealed.

https://github.com/pythonbyexample/PBE/tree/master/code/words.py

To run words, you will also need to download 'words', 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

NOTE that the 'words' file is a large collection taken from standard Ubuntu distribution and may
contain some inappropriate words, if you are under 18 make sure to ask your guardian before
playing the game; you can also replace the file with any word collection in the same format (one
word per line).

Word
----

The Word class needs to have the following functionality:

    - hide some letters of the word initially
    - display the word with hidden letters replaced with underscores
    - reveal a random letter
    - let player guess a letter

The `gen_hidden()` and `hide()` methods handle the initial hiding; hidden letter indexes are
stored in `self.hidden` list. When a letter is hidden, the same letter needs to be hidden
throughout the word (the same idea applies in reveal logic), which means the code is a bit more
complicated and that `initial_hide` setting is not applied precisely.

.. sourcecode:: python

    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def hide(self, index):
        """Hide all letters matching letter at `index`."""
        if index not in self.hidden:
            for n, nletter in enumerate(self.word):
                if nletter == self.word[index]:
                    self.hidden.append(n)

    def gen_hidden(self, hidden):
        """Hide letters according to `hidden`, e.g. if 0.7, hide 70%."""
        length       = len(self.word)
        num_to_hide  = round(length * hidden)
        letter_range = range(length)

        while len(self.hidden) < num_to_hide:
            self.hide(rndchoice(letter_range))


The following method displays the word along with the letter numbers; two small utility methods
provide length and spacing; `randreveal()` reveals a random hidden letter:

.. sourcecode:: python

    def __str__(self):
        word = ( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        return sjoin(word, space * self.spacing(), lettertpl)

    def __len__(self)    : return len(self.word)

    def spacing(self)    : return 2 if len(self) > 9 else 1
    def randreveal(self) : self.reveal( self.word[rndchoice(self.hidden)] )

The docstring here is hopefully clear enough:

.. sourcecode:: python

    def guess(self, i, letter):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if i in self.hidden and self.word[i] == letter:
            self.reveal(letter)

            L = [w for w in words if w.hidden and w != self]
            if L: rndchoice(L).randreveal()
            return True

    def reveal(self, letter):
        """Reveal all letters equal to `letter`."""
        for n, nletter in enumerate(self.word):
            if nletter == letter:
                self.hidden.remove(n)



Words
-----


Words class has the following functionality:

    - initialize a set of random words
    - small utility methods to iterate over words and get a specific words
    - display the list of words
    - reveal a random letter_range
    - let the user guess a letter
    - check if the game is finished and print win/lose message

The class has a few text template variables defined:

.. sourcecode:: python

    class Words(object):
        winmsg  = "Congratulations! You've revealed all words! (score: %d)"
        losemsg = "You've run out of guesses.."
        stattpl = "random reveals: %d | attempts: %d"

In the `__init__()`, I need to add random words to my list until I get the required number; I'm
excluding words of one and two chars because they are not interesting to guess.

.. sourcecode:: python

    def __init__(self, wordlist):
        self.random_reveals = random_reveals
        self.words          = set()

        while len(self.words) < num_words:
            word = Word( rndchoice(wordlist).rstrip() )
            if (limit9 and len(word)>9) or len(word) < 3:
                continue
            self.words.add(word)

        self.words   = list(self.words)
        self.guesses = sum(len(w) for w in self.words) // guesses_divby


The next two methods are used to get words (using words[index] notation) and to iterate over the
list ('for word in words'). The `display()` method needs to print out word and letter numbers, both
1-indexed.

.. sourcecode:: python

    def __getitem__(self, i) : return self.words[i]
    def __iter__(self)       : return iter(self.words)

    def display(self):
        print(nl*5)

        for n, word in enumerate1(self.words):
            print(lettertpl % n, space, word, nl)
            lnumbers = sjoin(range1(len(word)), space * word.spacing(), lettertpl)
            print(space*4, lnumbers, nl*2)

        print(self.stattpl % (self.random_reveals, self.guesses), nl)


The next two methods are higher-level handlers for the Word's `randreveal` and `guess` we've already
looked at; the last two check if the player won or lost and calculate the score which is based on
how many guesses he still had at the end.

.. sourcecode:: python

    def randreveal(self):
        if self.random_reveals:
            rndchoice( [w for w in self if w.hidden] ).randreveal()
            self.random_reveals -= 1

    def guess(self, word, lind, letter):
        if self.guesses and not self[word].guess(lind, letter):
            self.guesses -= 1

    def check_end(self):
        if not any(word.hidden for word in self):
            self.game_end(True)
        elif not (self.guesses or self.random_reveals):
            self.game_end(False)

    def game_end(self, won):
        self.display()
        msg = self.winmsg % (self.random_reveals*3 + self.guesses) if won else self.losemsg
        print(msg)
        sys.exit()


BasicInterface
--------------

The player can issue two different commands: 'word letter# letter' (eample: 32a for word 3, 2nd
letter is 'a') or 'r' for a random reveal. `TextInput` accepts a tuple of valid command patterns,
where '%hd' stands for human-entry number, which is adjusted for 0-indexing.

.. sourcecode:: python

    class BasicInterface(object):
        def run(self):
            self.textinput = TextInput(("%hd %hd %s", randcmd))

            while True:
                words.display()
                cmd = self.textinput.getinput()

                if first(cmd) == randcmd : words.randreveal()
                else                     : self.reveal_letter(*cmd)
                words.check_end()

        def reveal_letter(self, *cmd):
            try               : words.guess(*cmd)
            except IndexError : print(self.textinput.invalid_inp)


Configuration
-------------

A few options can be changed at the top of file: `num_words` sets the number of words used by the
game, `limit9` limits # of letters to 9, which makes it easier to input letter number and also
makes the display easier to read; the comments explain other options:

.. sourcecode:: python

    num_words      = 5
    hidden_char    = '_'
    lettertpl      = "%2s"
    initial_hide   = 0.7                # how much of the word to hide, 0.7 = 70%
    randcmd        = 'r'                # reveal random letter; must be one char
    limit9         = True               # only use 9-or-less letter words
    random_reveals = num_words // 2     # allow player to reveal x random letters

    wordsfn        = "words"

    guesses_divby  = 3      # calc allowed wrong guesses by dividing total # of letters by this number


Screenshots
-----------

Here is the sample run with a few letters already guessed by me::

    1    s  _  u  _  w  _  _  n  _

         1  2  3  4  5  6  7  8  9


    2    p  _  _  t  r  _

         1  2  3  4  5  6


    3    g  a  r  l  a  n  d

         1  2  3  4  5  6  7


    4    d  _  _  d  i  _

         1  2  3  4  5  6


    5    _  _  w  c  _  m  _  r

         1  2  3  4  5  6  7  8


    random reveals: 1 | attempts: 12
    >
