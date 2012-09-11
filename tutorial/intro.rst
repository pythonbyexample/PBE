Introduction
============

This guide is focused on introducing Python using two approaches: first,
with examples of simple yet practical and useful programs, and second, by
using Python to model some real-world systems and behaviors. The first
approach will, hopefully, act as a springboard for writing your own
programs. The second will serve to illustrate the subtle differences
between approaching real-life tasks and programming the computer to deal
with the same or similar tasks.

Requirements
------------

To use this guide, the minimal requirement is the `Python Interpreter <http://www.python.org/download/>`_, but I'd recommend also getting a good programming editor that support auto-indenting and syntax highlighting for Python, `wxPython <http://www.wxpython.org>`_ for GUI programming.

If you're completely new to Python and programming, it might be best to
start with the `Official Python Tutorial <http://docs.python.org/tutorial>`_.

Notes
-----

In the course of this guide I will run scripts directly as shown below, setting the executable flag beforehand (if you're on Linux):

.. sourcecode:: sh

    $ chmod u+x myscript.py
    $ ./myscript.py

Windows Notes
-------------

In windows you have to run python interpreter with the script as an argument:

.. sourcecode:: sh

    > python myscript.py

..or you can double-click the script in Windows Explorer.

If your script does some processing and then exits, and you run your scripts from Windows Explorer, you can add a line at the end that will let you know that the script finished and ask you to hit Enter to terminate script:

.. sourcecode:: python

    # ...

    raw_input("Done.. Hit Enter to exit ")
