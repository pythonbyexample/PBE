Achief
======

This little program will let you easily gamify tasks and activities, tracking progress with
points, levels, ranks and badges.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/achief.py


To run Achief, you will also need to download 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/utils.py


Task
----

This class will represent a single task/activity. It will keep track of points, levels, ranks and
will generate basic and advanced badges. The display method simply shows the task's data and the
badges via `get_badges` method. The `add()` method adds `n` points (the number may be negative, allowing
you to correct mistakes in entry). If rank is calculated beyond the range of the list of ranks, it
defaults to the last one.

.. sourcecode:: python

    ranks           = "Page Squire Knight-Errant Knight Minister Chancellor Imperator".split()
    badges          = '𝅪𝅫𝅬❖'
    fullbadge       = badges[-1]
    adv_badges      = ('✬', 'ਠ', 'હ', 'ತ')
    badge_modifier  = 1                      # set higher to get badges quicker
    levels_per_rank = 200

    class Task(object):
        points = 0
        tpl    = "[%d] level %d | %s\n"

        def add(self, n=1):
            self.points = max(0, self.points + n)
            self.level  = 1 + self.points // 10
            self.rank   = getitem(ranks, self.level // levels_per_rank, default=ranks[-1])

        def display(self):
            print(self.tpl % (self.points, self.level, self.rank))
            print(self.get_badges(self.level), nl)


The general idea for the badge system is that a level corresponds to a single basic badge, four
levels make a 'full' basic badge, three full badges are upgraded to one first-level advanced
badge. Advanced badges fill out in the form of a pyramid, with one highest level badge, two on the
next level, three on the level below and so on, so that the exact numbers depend on the number of
specified advanced badges. Once the pyramid is filled out, you can continue to add more points and
more top-level badges will be added.

If this sounds a bit confusing, look in the screenshot section for an example.

Also don't forget to look at the comments in the code below:

.. sourcecode:: python

    def get_badges(self, level):
        level = iround(level*badge_modifier)
        lines = self.advanced_badges(level) + [ self.basic_badges(level) ]
        lines = [space.join(line) for line in lines]

        return nl.join(l.center(16) for l in lines if l)

    def basic_badges(self, level):
        blvl = level % 12

        # number of full basic badges, level of last basic badge (may be 1,2,3 notches)
        num_full, last_badge = blvl//4, blvl%4

        last_badge = badges[last_badge-1] if last_badge else ''
        return fullbadge * num_full + last_badge

    def advanced_badges(self, level):
        """Complete pyramid is filled out at level=1339."""
        num_levels = len(adv_badges)
        blevels    = [0] * num_levels   # number of adv. badges at each level
        blevels[0] = level // 12

        for n, levels in enumerate(blevels[:-1]):
            max_badges = num_levels - n + 1
            blevels[n+1], blevels[n] = blevels[n] // max_badges, blevels[n] % max_badges

        numbered = reversed(list(enumerate(blevels)))
        return [adv_badges[n] * count for n, count in numbered]

Tasks
-----

The `Tasks` class works as an interface for accessing specific tasks by their names. In the
`__init__()` method, I'll need to load tasks from the shelve file, creating a
`collections.defaultdict` if the shelve is newly created. The default dict will create a new `Task`
automatically when I try to access it.

.. sourcecode:: python

    class Tasks(object):
        tpl = " %-15s %7s %7s %20s"

        def __init__(self):
            data  = shelve.open(os.path.expanduser(savefn), writeback=True)
            if "tasks" not in data:
                data["tasks"] = defaultdict(Task)

            self.tasks = data.get("tasks")
            self.data  = data

        def delete(self, name):
            if name in self.tasks:
                del self.tasks[name]
                print("'%s' deleted" % name)

        def show(self, name):
            if name in self.tasks:
                self.tasks[name].display()

        def add(self, name, n=1):
            """Add `n` points to `name` task."""
            self.tasks[name].add(n)
            self.show(name)

        def list(self):
            print(self.tpl % ("task", "points", "level", "rank"), nl + div)
            for name, task in sorted(self.tasks.items()):
                print(self.tpl % (name, task.points, task.level, task.rank))

        def close(self):
            self.data.close()

ArgumentParser
--------------

I will use the `argparse.ArgumentParser` class to help me handle the command-line argument. The
following is the auto-generated help message, it should help you understand the `add_argument()`
lines below:

Note that I use `nargs='?'` for positional args because I want to make them optional, also note that
`points` type is 'int', and that `list` action is 'store_true', which means it needs no value and
simply stores `list=True` when present on the command line.

.. sourcecode:: python

    tasks  = Tasks()
    parser = ArgumentParser()

    parser.add_argument("task", default=None, nargs='?')
    parser.add_argument("points", type=int, default=1, nargs='?')

    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-s", "--show", metavar="TASK", default=False)
    parser.add_argument('-d', "--delete", metavar="TASK", default=False)
    args = parser.parse_args()

    if   args.delete   : tasks.delete(args.delete)
    elif args.show     : tasks.show(args.show)
    elif args.list     : tasks.list()
    elif args.task     : tasks.add(args.task, args.points)
    tasks.close()

Configuration
-------------

You can change the ranks, badges and advanced badges to other values; levels per rank is set at
200 to give you the highest rank as you get close to filling out the entire pyramid of badges; if
you change the # of advanced badges, you should also adjust this setting.

.. sourcecode:: python

    savefn          = "~/.achief.dat"
    ranks           = "Page Squire Knight-Errant Knight Minister Chancellor Imperator".split()

    div             = '-' * 60
    badges          = '𝅪𝅫𝅬❖'
    fullbadge       = badges[-1]
    adv_badges      = ('✬', 'ਠ', 'હ', 'ತ')
    badge_modifier  = 1                      # set higher to get badges quicker
    levels_per_rank = 200


Screenshots
-----------

Just as an example, if I want to track learning of Python, I can add a single point for every 15
minutes, or 3 points for 15 minutes, if I want badges to add up faster::

    $ achief.py python
    [1] level 1 | Page

           𝅪

    $ achief.py python 4
    [5] level 1 | Page

           𝅪

    $ achief.py python 25
    [30] level 4 | Page

           ❖

    $ achief.py python 25
    [55] level 6 | Page

          ❖ 𝅫

    $ achief.py python 900
    [955] level 96 | Page

           ਠ
         ✬ ✬ ✬

    $ achief.py python 920
    [1875] level 188 | Page

         ਠ ਠ ਠ
          ❖ ❖

    $ achief.py python 1325
    [3200] level 321 | Squire

           હ
           ਠ
           ✬
         ❖ ❖ 𝅪

    $ achief.py learn-kungfu
    [1] level 1 | Page

           𝅪

    $ achief.py learn-kungfu 5500
    [5501] level 551 | Knight-Errant

          હ હ
           ਠ
         ❖ ❖ 𝅬

I can also provide negative number to adjust the total; and use -l argument to list::

    achief.py python -20
    [3180] level 319 | Squire

           હ
           ਠ
           ✬
          ❖ 𝅬


    $ achief.py -l
     task             points   level                 rank
    ------------------------------------------------------------
     learn-kungfu       5501     551        Knight-Errant
     python             3180     320               Squire
