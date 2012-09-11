.. role:: raw-html(raw)
    :format: html

Chapter 02
==========
:raw-html:`<div style="float:right; width:400px; text-align:right; font-style:italic; font-size:80%;">The most important single aspect of software development is to be clear about what you are trying to build.
<p style="text-align:right;">- Bjarne Stroustrup</div>`

:raw-html:`<br><br><br><br>`

Sig rotator
-----------

Signature rotator is a fun, simple, and, who knows, maybe even useful script we'll look at in this chapter. If you ever send emails or post newsgroup messages, it can put amusing or enlightening ditties under your message. The general idea is to have a source file with any number of random signatures separated by some sort of a divider (I will use '---'); the rotator script will load them into a list and then choose & return one randomly. (Note that not all email programs will let you use a script as a source of signature.)

`sigs.txt <_static/sigs.txt>`_

.. literalinclude:: .static/sigs.txt

`rotate.py <_static/rotate.py>`_

.. literalinclude:: .static/rotate.py

.. sourcecode:: sh

    $ ./rotate.py
    --
    To knock a thing down, especially if it is cocked at an arrogant angle, is
    a deep delight of the blood. 
     - George Santayana

Batch File Renamer
------------------

Quick-and-dirty batch file renamer: sometimes files just aren't named right and there's too many of them. From now on, you will no longer need to aggravate your carpal tunnel every time you have to rename ten thousand files. For the first example, let's say we have files named like band-name.mp3, and we need to add spaces around the dash. We'll accept directory name as the only argument and rename files in all subdirectories.

`rename.py <_static/rename.py>`_

.. literalinclude:: .static/rename.py

.. sourcecode:: sh

    $ ls doors
    doors-a crystal ship.mp3 doors-the end.mp3
    $ ./rename.py doors
    renamed doors-a crystal ship.mp3 -> doors - a crystal ship.mp3
    renamed doors-the end.mp3 -> doors - the end.mp3

Normally we'd test if we did get an argument and print an error if not, but the beauty of these small scripts for personal use you can skip error-checking for simplicity since you are familiar with the script. In this guide I will typically not do error checking in order to concentrate on main functionality, except for cases when this may lead to data loss or other serious errors.

Let's think of a more complicated example where the file name might look like '3) song (remix).mp3' but some files don't have the round bracket after song number. You can't simply replace it with a space and dash, you need to check if it's in the beginning of filename and only replace it once.

Here's the changed visit function:

`rename2.py <_static/rename2.py>`_

.. sourcecode:: python

    def visit(arg, dirname, names):
        for name in names:
            if ")" in name[:2]:
                newname = name.replace(")", " -", 1)    # replace first instance
                fn = os.path.join(dirname, name)
                newfn = os.path.join(dirname, newname)
                os.rename(fn, newfn)
                print "renamed '%s' -> '%s'" % (name, newname)

.. sourcecode:: sh

    $ ls moogwai
    3) moogwai - viola (remix).mp3
    $ ./rename.py moogwai
    renamed '3) moogwai - viola (remix).mp3' -> '3 - moogwai - viola (remix).mp3'

Site Templating Program
-----------------------

You have a website, you have some content that cries to be shared with the world, but you want to be able to change the look of shared elements, i.e. the header, footer, logo and perhaps something else easily without going to each and every page. You also wish that content pages were simpler and smaller, they should only have content specific to each page. In addition, you'd like a script to automatically generate 'next' and 'previous' links, and why not build the index page while we're at it? It would also be useful to turn off the index-building easily because you might want something more involved than a plain list of links for the index page.

The plan is to have a subdirectory with content pages and have a template file; the script will load each content page, insert it into the template, insert next/previous links and write out a finished file; finally it will generate and write out an index page.

First, let's do simple insertion without index or links.

Our pseudo-code::

    * template = template_file.read()
    * content_page_list = ..
    * for page in content_page_list:
        * title = page.capitalize_words()   # use filename as title of page
        * content = page.read_from_file()
        * output = template.replace("[title]", title)
        * output = template.replace("[content]", content)
        * output.write_file()

`mksite.py <_static/mksite.py>`_

.. literalinclude:: .static/mksite.py

`template.html <_static/template.html>`_

.. literalinclude:: .static/template.html

`style.css <_static/style.css>`_

.. literalinclude:: .static/style.css

Now we can make directory 'content' and put a content page there:

`page1.html <_static/content/page1.html>`_

.. literalinclude:: .static/content/page1.html

..and we have everything in place to run mksite.py:

.. sourcecode:: sh

    $ ./mksite.py
    processing file page1.html
    
You can follow the link to look at the processed page:

`Page 1 <_static/page1.html>`_
