#!/usr/bin/env python

import sys


class Branch(object):
    """Conversation branch."""
    auto_ids = 2, 3     # automatic events, see below
    options  = None
    player   = False

    def __init__(self, text, *args):
        self.text = text
        self.id   = None
        if args and isinstance(args[0], int):
            self.id, args = args[0], args[1:]

        if args:
            self.options = args
        elif self.id not in self.auto_ids:
            self.options = (Branch("I want to ask about something else..", 2),
                            Branch("<Done>", 3))

    def __str__(self):
        return str(self.text) if self.text else "<id=%s>" % self.id

    def __getitem__(self, n):
        return self.options[n]

class Nbranch(Branch): pass
class Pbranch(Branch): player = True


class JacobConversation(object):
    done = False

    handlers = {
        1 : "greet",
        2 : "back",
        3 : "done",

        4 : "chest",
        5 : "chest_accept",
    }

    greetings = ("Howdy, Stranger", "Have you gotten around to doing this small favor for me yet?",
                 "Thanks, fella!", "Howdy!")

    tree = Nbranch(None, 1,
               Pbranch("Have you heard any news lately?",
                  Nbranch("There is a new sheriff in town..")),

               Pbranch("Can I find any work in this town?",
                  Nbranch("They might have some work posted at the Rusty Rose Pub.."),
                  Nbranch("Say, I might have something for you.. there is a chest in the next "
                          "room, maybe you could bring it to me?", 4,
                     Pbranch("Yes",
                        Nbranch("Good, it's in the room right over there, too heavy for me "
                                "to lift.. much obliged!", 5)
                        ),
                     Pbranch("No")
                     )
                  )
               )

    def greet_init(self, conv):
        """Initial greeting."""
        greet = self.greetings

        if not conv.npc.met_player:
            conv.npc.met_player = True
            return greet[0]

        elif not quests.chest.done:
            pinv, ninv = conv.player.inventory, conv.npc.inventory
            if chest in pinv:
                pinv.remove(chest)
                ninv.append(chest)
                return greet[2]
            return greet[1]

        else:
            return greet[3]

    def chest_filter(self, conv):
        """Check if player qualifies for chest quest."""
        return bool(conv.player.strength >= 5 and conv.player.charisma >= 5 and not quests.chest.done)

    def back_after(self, conv):
        conv.branch = self.tree

    def done_after(self, conv):
        conv.done = True

    def chest_accept_after(self, conv):
        """Player accepted chest quest."""
        rooms[1].unlock()


class Character(object):
    gold = 0

    def __init__(self):
        self.inventory = []

class Player(Character):
    strength = 5
    charisma = 5

class Jacob(Character):
    met_player   = False
    conversation = JacobConversation()

class Room(object):
    locked = False

    def __init__(self, *items):
        self.contents = items

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

class Chest(object):
    pass


class Conversation(object):
    done = False

    def __init__(self, player, npc):
        self.branch       = None
        self.player       = player
        self.npc          = npc
        self.conversation = npc.conversation

    def process_option(self, option, stage):
        """If there is a handler method for the option, run it; otherwise return True."""
        name = self.conversation.handlers.get(option.id, '')
        handler = getattr(self.conversation, name + '_' + stage, None)
        return handler(self) if handler else True

    def init_option(self, option): return self.process_option(option, "init")
    def filter_option(self, option): return self.process_option(option, "filter")
    def after_option(self, option): return self.process_option(option, "after")

    def get_branch(self):
        branch      = self.branch or self.conversation.tree
        text        = [branch.text or self.init_option(branch), '']
        self.opts   = [o for o in branch.options if self.filter_option(o)]
        self.branch = branch

        for n, b in enumerate(self.opts):
            text.append( "%d) %s" % (n+1, b.text) )
        return '\n'.join(text) + '\n'

    def next(self, n=0):
        """Descend to `n` branch in current branch's `options`."""
        self.branch = self.branch[n]
        return self.branch

    def answer(self, n):
        """Process selected answer branch and descend to the next NPC branch."""
        self.after_option(self.next(n-1))
        if self.done:
            return None
        if self.branch.player:
            self.next()
        return True

def test():
    player = Player()
    jacob  = Jacob()
    conv   = Conversation(player, jacob)
    chest  = Chest()
    rooms  = Room(), Room(chest)

    while 1:
        print(conv.get_branch())
        n = int(raw_input('> '))
        if not conv.answer(n):
            break


if __name__ == "__main__":
    try: test()
    except KeyboardInterrupt: sys.exit()
