.. role:: raw-html(raw)
    :format: html

Chapter 04
==========
:raw-html:`<div style="float:right; width:400px; text-align:right; font-style:italic; font-size:80%;">Dreams are the touchstones of our characters.
<p style="text-align:right;">- Henry David Thoreau, Walden</div>`

:raw-html:`<br><br><br><br>`

Multiple Choice Test
--------------------

The pseudo-code is listed below:

::

    * list: [['question', 'answer1', 'answer2', 'answer3', num]] 
      - num is the number of right answer
    * infinite loop:
        * pick random question
        * list choices
        * ask for answer
        * print 'Right' or 'Wrong' 


Here is the actual Python code:

`mchoice.py <_static/mchoice.py>`_

.. literalinclude:: .static/mchoice.py

That's all there is to it --- most of this code should be fairly clear; `random..choice(lst)` returns a random item out of list `lst`,  `enumerate()` takes a sequence and returns pairs of items and their sequence numbers.

Flash Cards
-----------

Flash cards are a popular way of memorizing a large number of morsels of information. At times it might be useful to have virtual flash cards in a program --- for example, if you're plucking the information from websites or an e-book. In this section we'll make an easy flash cards program; if you want the results to look more like real flash cards, you may want to change the size of font of the terminal where the program will run.

Our pseudo-code will go as follows::

    * read flash cards from a text file
    * display random card
    * after Enter is pressed, display the answer
    
..and the Python code:

`flashcards.py <_static/flashcards.py>`_

.. literalinclude:: .static/flashcards.py

`flash-cards.txt <_static/flash-cards.txt>`_

.. literalinclude:: .static/flash-cards.txt

The following listing is a small refinement of flash cards where we factor
out card printing into a separate function --- this will allow us to edit
only one location instead of two when we need to change card display code.

`flashcards2.py <_static/flashcards2.py>`_

.. literalinclude:: .static/flashcards2.py

Simple Database
---------------

Industrial-strength databases have to be extremely fast and powerful but
for many simple database-like tasks neither requirement is crucial. In this
section we'll make a simple database of music collection.
