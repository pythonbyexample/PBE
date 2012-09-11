.. role:: raw-html(raw)
    :format: html

Chapter 03
==========
:raw-html:`<div style="float:right; width:400px; text-align:right; font-style:italic; font-size:80%;">If you would know the flavor of hucklebberries, ask the cow-boy or the partridge.
<p style="text-align:right;">- Henry David Thoreau, Walden</div>`

:raw-html:`<br><br><br><br>`

Break Reminder
--------------

You may have seen programs that monitor your use of computer and remind you to take a break at time intervals. In this chapter we'll try to roll our own. The basic functionality is very easy to accomplish: we need to make a loop that sleeps for a specified number of minutes and then we'll do a visual and audio alarm.

First, to take things one step at a time, we'll do a version with just the visual alarm (in pseudo-code)::

    * infinite loop:
        * print "Work!"
        * sleep for 'work interval'
        * loop for number of seconds in break interval:
            * blink "Take it easy!"


..and in Python code:

`breminder.py <_static/breminder.py>`_

.. literalinclude:: .static/breminder.py

We already covered `\\r` code and `flush()` in Chapter 1, refer to that
chapter for the explanation if you skipped it.

The following line may be a little confusing:

.. sourcecode:: python

    for y in range( int(break_interval*60) ):
    
Our goal here is to loop and keep blinking with "Take a break" message,
therefore we need to loop for as many times as there are seconds in break
interval, and that is precisely what `for` statement does --- it loops a
given number of times and stores loop number in `y` variable, starting at
0, then 1, 2, 3 and so on.

In the following example we'll add a few beeps at the beginning of each
break. If you're using windows you can play a .wav sound file just as
easily using the `winsound` module; with linux there isn't a built-in
way of playing a sound file but you can call an external program like
`mpg321` to play an mp3 file, for instance.


`breminder2.py <_static/breminder2.py>`_

.. sourcecode:: python

    # ...

    if sys.platform.startswith("win"):
        import winsound
        is_win = True
    else:
        is_win = False

    # in reminder():

    time.sleep(60*work_interval)
    for y in range(3):
        if is_win:
            # frequency in hz, length in 1/1000 secs
            winsound.Beep(1000,300) 
        else:
            print "\a"
        time.sleep(0.3)

    # ...

One last refinement we'll make to our program is microbreaks --- regular
breaks will be much longer and farther apart and the microbreaks are just
long enough to allow you to stretch and close your eyes for a few
seconds. Pseudo-code is as follows::

    * num_micro_breaks - number of micro-breaks between full breaks
    * mbreaks - # of micro-breaks since last full break
    * 
    * infinite loop:
        * print "Work!"
        * sleep for 'work interval'
        * if mbreaks => num_micro_breaks:
            * Run full break
            * mbreaks = 0
        * else:
            * Run micro-break
            * mbreaks += 1

..in Python-speak:

`breminder3.py <_static/breminder3.py>`_

.. sourcecode:: python

    # ...
    fbreak_interval = 0.5
    mbreak_interval = 0.1

    num_micro_breaks = 2

    # in reminder():

    if mbreaks >= num_micro_breaks:
        break_interval = fbreak_interval
        mbreaks = 0
    else:
        break_interval = mbreak_interval
        mbreaks += 1

    for y in range( int(break_interval*60) ):
        print "\r############# %s (%s) ################" % (msg, y),
        # ...

.. note::

    With a bit of inventiveness, you can use the terminal for things that you would normally need a GUI program. For example, if you want a more eye-grabbing visual alert, you can print 25 rows of '#' characters, sleep for half a second, print 25 rows of blank spaces, and so on.


GUI versions of break reminder and timer
----------------------------------------

You can stretch terminal programs very far and, indeed, in terms of maintainability and flexibility for personal projects, simple terminal interfaces are hard to beat. And yet, one fine day you're bound to notice that for a certain task, terminal is just not good enough and that you finally want to make a neat GUI programs just like Adobe or Autodesk do.

In this section I will briefly show how to make a very basic --- but still useful --- GUI app. Before you look at the code, I should mention that timers in GUI programs work somewhat differently: in console we do something, then sleep for x seconds, then do something again, and so on; in GUI programs that would not work well because when you sleep, the whole GUI would be unresponsive, it would not update visually and button presses would be ignored. Obviously, that's not acceptable. Instead, we have to set up a timer that calls a specified function at specified intervals, the function in question is responsible for checking for some sort of condition to stop its operations when it's done. 

In some cases it's more convenient to set up a timer that calls a function only once after a specified amount of time passed.

The first way to set up a timer is as shown below:

.. sourcecode:: python

    self.timer = wx.PyTimer(self.RunTimer)
    self.timer.Start(1000)

..where `RunTimer()` is a function that does some work and calls `self.timer.Stop()` when it's done. Time is given in ms, 1000 as shown here stands for 1 second. The second way of setting a timer:

.. sourcecode:: python

    wx.CallLater(1000, myfunction)

Pseudo-code for our GUI timer::
    
    * timer class:
        * initialize:
            * create time display area
            * create stop button
            * create time entry area
            * create start button
            * create progress bar

        * Start function (runs when 'start' is clicked):
            * stop timer and countdown if they're running
            * if time entry field has contents, run StartCountdown function
            * otherwise, start simple timer (RunTimer function)

        * StartCountdown function
            * parse time from time entry field
            * start countdown (RunCountdown function)

        * Stop function
            * stop timer and countdown, reset time display, reset background
              to white color

        * RunTimer function
            * update time display with elapsed time

        * RunCountdown function
            * update time display
            * update progress bar
            * stop countdown and run alarm() function if countdown is finished

        * Alarm function
            * start alarm timer that calls function ToggleBG() every 200ms

        * ToggleBG function
            * if alarm started more than 5 seconds ago: stop alarm timer
            * if text display background is white, set to green, otherwise
              set to white

    * Operation:
        * simple timer:
            * user clicks on start button, Start() function runs, creates 
              timer that repeatedly calls RunTimer() function
            * user clicks on stop button, Stop() function stops the timer

        * countdown timer:
            * user enters time and clicks 'Start', Start() function runs
              StartCountdown() function which creates countdown timer, 
              repeatedly calling RunCountdown()
            * when countdown time runs out, RunCountdown() stops timer and 
              calls Alarm(), which starts alarm timer that calls ToggleBG()
              every 200ms for 5 seconds, then stops alarm timer.

Here's how it will look (time entry field is not visible but it's there, above the "start" button):

.. image:: .static/gtimer2.gif

I'm sure you will appreciate how simple and concize is the code for console programs once you look over this listing for GUI code:

`gtimer.py <_static/gtimer.py>`_

.. literalinclude:: .static/gtimer.py

A lot of this is simply template GUI program code that will always have to be there and we won't go into what each and every line does. Some of the code does need explanation, however.

The general idea behind GUI programs is that you create buttons and pulldown menus and bind each of them to a separate function; when you press the button, the function runs and checks the state of environment --- i.e. whether some settings are on or off, toggle buttons are set, etc --- and then it will "do stuff", and whatever magic needs to happen, happens. There is really not that much difference compared to a console program: instead of asking user for input and then running a function based on that, you simply wait for a button press.

Much of the complexity of GUI programs is due to flexibility of presentation and layout. You can do more --- which is why, after all, GUI programs are so much more popular nowadays --- and you have to pay the price for this additional complexity.

One of the challenges of GUI design is placement of various widgets in the window in a way that lines up, looks nice and changes properly when the window is resized. There are different ways to do that in wxPython but the most widespread method is to use something called *sizers*. Sizers are containers that can be set to expand in various ways, one sizer can be put in another sizer, they can be aligned to the sides, top or bottom, or centered.

It's a bit tricky to visualize which sizers you need and where they should go in your head --- I highly recommend drawing a simple diagram beforehand. In our case we need a time display on the left side, large stop button to the right of it, time entry field futher to the right and a start button under the time entry so that the last 2 elements together are the same height as the stop button. Finally, there is a progress bar on the bottom, taking up the full width of the window.

.. image:: .static/gtimer1.gif

The outermost sizer --- let's call it `osizer`, will hold everything else. There are two types of sizers: horizontal and vertical, in the first type contents are stacked to the right as they're added, in second type --- to the bottom. Since we need to stack progress bar on the bottom, we'll use vertical sizer here.

It doesn't matter in what order you create sizers and add items to them. You can create all sizers at the top, then create each widget and add it to the relevant sizer, or you can first create all widgets then, at the bottom, create all sizers and first add widgets to innermost sizers than add these sizers to outer sizers, or do some combination of these approaches. It really does not matter much in terms of clarity; I find that they only way to make sizer layout clear is to make a hand-drawn diagram and refer to it as you add sizers to your code, without a diagram even the simplest layout can be tricky to visualize.

Adding Settings Screen
----------------------

Few programs can be useful without some way to change options. Since this is a tiny timer program for our own use we could get by with a simple txt options file, but why settle for less when we can have a professional slick GUI settings screen like in the best software houses of Europe? The answer is: "No reason".

Our game plan is::

    * Preferences window
        * initialize
            * color picker
            * ok button - bind to OnOk function
            * cancel button - bind to OnCancel function

        * OnOk() - get color from color picker, set parent frame's alarm color var

        * OnCancel() - close Preferences window


    * Main window
        * initialize
            * create menu bar with 'edit' menu and 'preferences' button
            * bind preferences button to EditPreferences function

        * EditPreferences() - create and show Preferences Window


..and here is how it's done:

`gtimer2.py <_static/gtimer2.py>`_

.. sourcecode:: python

    # Create menu bar, edit menu and preferences menu button
    menu = wx.Menu()
    menu_edit = menu.Append(300, "&Preferences", "Edit Preferences")
    wx.EVT_MENU(self, 300, self.EditPreferences)
    menuBar = wx.MenuBar()
    menuBar.Append(menu, "&Edit")
    self.SetMenuBar(menuBar)

    # ...

    # preferences function:
    def EditPreferences(self, event):
        frame = Preferences(self)
        frame.Show()

    # ...

    # preferences window class:
    class Preferences(wx.Frame):
        """Main settings class."""
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, 'Preferences', size=(50,50),
                style=wx.DEFAULT_FRAME_STYLE |
                wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW ^ 
                wx.RESIZE_BORDER)
            osizer = wx.BoxSizer(wx.VERTICAL)
            osizer2 = wx.BoxSizer(wx.VERTICAL)
            sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            sizer2 = wx.BoxSizer(wx.HORIZONTAL)

            self.parent = parent
            lbl = wx.StaticText(self, -1, "Alarm Color")
            # ac = parent.alarm_color
            self.cp = csel.ColourSelect(self, -1, None, parent.alarm_color)

            sizer1.Add(lbl, 0, wx.ALIGN_CENTER, border=5)
            sizer1.Add((4,4), 0, wx.ALL, border=5)
            sizer1.Add(self.cp, 0, wx.ALIGN_CENTER, border=5)

            buttonOK = wx.Button(self, 301, label="OK", size=(80,24))
            wx.EVT_BUTTON(self, 301, self.OnOK)
            sizer2.Add(buttonOK, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
            buttonC = wx.Button(self, 302, label="Cancel", size=(80,24))
            wx.EVT_BUTTON(self, 302, self.OnCancel)
            sizer2.Add(buttonC, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

            osizer.Add(sizer1, 1, wx.ALIGN_TOP)
            osizer.Add(sizer2, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, border=5)
            osizer2.Add(osizer, 0, wx.ALL, border=5)

            self.SetSizer(osizer2)
            self.Fit()

        def OnOK(self, event):
            self.parent.alarm_color = self.cp.GetValue()
            self.Close(True)

        def OnCancel(self, event):
            self.Close(True)
