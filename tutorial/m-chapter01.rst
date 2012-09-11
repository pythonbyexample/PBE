.. role:: raw-html(raw)
    :format: html

Chapter 01
==========

:raw-html:`<div style="float:right; width:400px; text-align:right; font-style:italic; font-size:80%;">These machines have no common sense; they have not yet learned to "think," and they do exactly as they are told, no more and no less. This fact is the hardest concept to grasp when one first tries to use a computer. 
<p style="text-align:right;">- Donald Knuth</div>`

:raw-html:`<p><p><p><br><br><br><br><br><br>`

The goal of this guide is to teach Python by building simple, practical, useful programs: timer programs, break reminder, a game, a gui program and more.

The first example program will be a simple timer that will be started from the command line and stopped with a **Ctrl-C** shortcut. In pseudocode, what we need to do is this::

    * function format_time(seconds)
        * return a string of the form "hours:minutes:seconds"
    * start = current time
    * loop:
        * elapsed time = current time - start
        * print format_time(elapsed time)
        * sleep 1 second

Here is the implementation in real python code:

`timer.py <_static/timer.py>`_

.. literalinclude:: .static/timer.py

.. sourcecode:: sh

    $ ./timer.py
    0:25

This example is the most basic timer program that you can run from command line. It will update elapsed time display every second and terminate when you hit Ctrl-C. And yet it can be useful because it's not included as part of most Operating Systems and has an advantage over many other timer programs and electronic timers in that you will be able to see history of times you recorded as you use it.

An additional advantage is that you know how it works, have the code and therefore can change it as you see fit.

Most of this code should be clear enough. When we need to split seconds into minutes and remaining seconds, we use division and modulus operators --- division will yield whole number of minutes. If you ever need to get a fractional --- a floating point number --- one of the numbers needs to be a float. You can convert an integer to a float using `float()` function. Modulus operator (%) will give you the remainder of the division.

`"\\r..."` format code at the beginning of a string returns to the biginning of the line and the rest of string overwrites old contents of the line. 

There's one other little trick we need to use to update time display: Python does not print out the line to physical screen until it gets the newline character, (for performance reasons), and yet we can't print newline because then caret would go to the next line and we can't go back --- what we need to do is to put a comma after the print statement to omit a newline character:

.. sourcecode:: python

    print "Don't want no newline!",

..and then we have to use `flush()` function to print all of that to screen without going over to the next line:

.. sourcecode:: python

    sys.stdout.flush()

`zfill(n)` string method will add zeroes to expand the string to `n` length.

`try: ... except KeyboardInterrupt:` construct will exit cleanly when you hit Ctrl-C to stop the timer.

`if __name__ == "__main__":` block will not run if this file is imported by another module, but will run otherwise. This is very useful to let other programs use functionality contained here without running the actual timer.

Here is an extended version of timer that adds a countdown function in pseudocode::

    * function countdown(time_string)
        * example time_string: "4:30" - 4 min 30 sec
        * split string into minutes, seconds, (hours if given) - still 
        * time left = seconds left
        * loop:
            * print format_time(time left)
            * sleep 1 second
            * if no time left, print 'Done!' and return
            * time left -= 1 second

    * if got 1 argument: run countdown(arg#2)
    * if got no arguments: run regular timer as before

The following code implements it in python:

`timer2.py <_static/timer2.py>`_

.. sourcecode:: python

    ...

    def countdown(to):
        """Run a countdown timer, arg ans should be a string in the form
        of m:s or h:m:s"""
        t = to.split(":")
        h = m = 0
        if len(t) == 2:
            m, s = t
            m = int(m); s = int(s)
        elif len(t) == 3:
            h, m, s = t
            m = int(m); s = int(s)
            h = int(h)
        else:
            print "Error parsing countdown time, try again.."
            return

        left = s + m*60 + h*60*60

        try:
            while 1:
                print "\r" + ftime(left),
                sys.stdout.flush()
                time.sleep(1)
                if left <= 0:
                    print "DONE!"
                    return
                left -= 1
        except KeyboardInterrupt:
            print
            return


    if __name__ == "__main__":
        if len(sys.argv) == 2:
            countdown(sys.argv[1])  # there is a second argument, giving countdown time,
                                    # pass it on to countdown() function
        else:                       # otherwise run normal timer
            start = time.time() 
            try:
                while 1:
                    elapsed = time.time() - start
                    print "\r" + ftime(elapsed),
                    sys.stdout.flush()
                    time.sleep(1)
            except KeyboardInterrupt:
                sys.exit()


.. sourcecode:: sh

    $ ./timer2.py 0:20
    0:00 DONE!


One last touch is to add a beep() function that will alert you when countdown is finished:

`timer3.py <_static/timer3.py>`_

.. sourcecode:: python

    def beep():
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(1000,300) # frequency in hz, length in 1/1000 secs
        else:
            # in linux, etc
            print "\a"

    # ... in countdown(): ...

        if left <= 0:
            beep()
            return


..and call beep() instead of printing 'DONE!'.

Now we can add some unusual features. What if I want to specify several different countdowns from the start and have my script do them in sequence? Only a three lines' change will do:

`timer4.py <_static/timer4.py>`_

.. sourcecode:: python

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            countdown(arg)          # there is a second argument, giving countdown time,

.. sourcecode:: sh

    $ ./timer4.py 0:20 0:5 0:8
    [...]
    0:00

How about running a continuous countdowns to the same time until stopped? We need to change the code as follows:

`timer5.py <_static/timer5.py>`_

.. sourcecode:: python

    # in countdown():
    try:
        while 1:
            print "\r" + ftime(left),

    # ...

    except KeyboardInterrupt:
        sys.exit()

    # ...

    if sys.argv[1] == "-c":
        arg = sys.argv[2]
        while 1:
            countdown(arg)
    else:
        for arg in sys.argv[1:]:
            countdown(arg)      # there is a second argument, giving countdown time,

.. sourcecode:: sh

    $ ./timer5.py -c 30:0
    [...]
    0:00

Other things we could easily do would be changing the number of beeps, using a wav sound instead of beeps.

Once you have a certain level of complexity it makes sense to switch to a UI that gives you an in-program command line instead of forcing you to use multiple argument switches. Here is an example of our timer program with such an interface:

`timer6.py <_static/timer6.py>`_

.. sourcecode:: python

    def main():
        print """
        Commands:
        s       - start timer
        c m:s   - count down timer (e.g. c 5:30)
        q       - quit

        stop timer by pressing Ctrl-C
        """

        while 1:
            ans = raw_input("> ")
            if ans == "s":
                timer()
            elif ans.startswith("c "):
                countdown(ans.split()[1])
            elif ans == "q":
                sys.exit()


    if __name__ == "__main__":
        main()

.. sourcecode:: sh

    $ ./timer6.py
    Commands:
    s       - start timer
    c m:s   - count down timer (e.g. c 5:30)
    q       - quit

    stop timer by pressing Ctrl-C
    > s
    0:35 
    > c 1:20
    0:00
    > q
