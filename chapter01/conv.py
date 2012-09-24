#!/usr/bin/env python

class Branch(object):
    def __init__(self, text, *args, id=None):
        self.id      = id
        self.text    = text
        self.options = args

conv1 = Branch("Howdy, Stranger", id=0,
               Branch("Have you heard any news lately?",
                      Branch("There is a new sheriff in town.."),),

               Branch("Can I find any work in this town?",
                      Branch("They might have some work posted in the Saloon, check there."),
                      Branch("Say I might have something for you.. there is a chest in the next "
                             "room, maybe you could bring it to me?", id=1,
                             Branch("Yes",
                                    Branch("Good, it's in the room right over there, too heavy for me "
                                           "to lift.. much obliged!", id=2)
                                    ),
                             Branch("No")
                             )
                      )
               )

class Conversation(object):
    handlers = dict(
                    1 = "chest_test",
                    2 = "chest_accept",
    )

    def __init__(self, player, npc, branches):
        self.player   = player
        self.npc      = npc
        self.branches = branches

    def chest_test_check(self):
        return bool(self.player.strength >= 5 and self.player.charisma >= 5)

    def chest_accept_process(self):
        rooms[1].unlock()

    def check_option(self, option):
        """If there is a check for the option, run it; otherwise return True."""
        check = getattr(self, self.handlers.get(option.id, '') + "_check", None)
        return check() if check else True

    def process_option(self, option):
        """If there is a process method for the option, run it."""
        process = getattr(self, self.handlers.get(option.id, '') + "_process", None)
        if process: process()

    def run(self):
        branch = self.branches
        while 1:
            print(branch.text)
            opts = [o for o in branch.options if self.check_option(o)]

            for n, b in enumerate(branch.options):
                print("%d) %s" % (n+1, b.text))
            n = int(raw_input('> ')) - 1
            branch = opts[n]
            self.process_option(branch)


if __name__ == "__main__":
    main()
