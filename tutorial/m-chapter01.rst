.. role:: raw-html(raw)
    :format: html

Versi - the Reversi (Othello) clone
===================================

:raw-html:`<div style="float:right; width:400px; text-align:right; font-style:italic; font-size:80%;">These machines have no common sense; they have not yet learned to "think," and they do exactly as they are told, no more and no less. This fact is the hardest concept to grasp when one first tries to use a computer. 
<p style="text-align:right;">- Donald Knuth</div>`

:raw-html:`<p><p><p><br><br><br><br><br><br>`

The goal of this guide is to teach Python, modular, object-oriented design and
PyGame framework.

The first game I'll write will be a simple Reversi clone.

You can look at the code here: `<`

The game will contain two large classes: Reversi and Board. Board class holds
the board structure where all the playing pieces are stored, it handles things
like checking if a move is valid, generating a list of captured pieces,
initializing the board, placing a new piece on the board and calculates scores.

The main Reversi class runs the main game loop, displays some gameplay-related
prompts, initializes resources.

In addition, there is a handful of smaller classes that will be used by the
first two: Player and Computer will make moves and will also keep track of
which colour player and computer are; both will be used by the Reversi class.

There will also be classes representing a location on board, a playing piece, a
hint and a blank tile -- all of these will be used by the Board class.

The Location class will provide convenient access to x,y coordinates of each
tile; Playing Piece will keep track of its colour and allow flipping to the
opposite colour; both Hint and Blank classes will simply draw themselves on the
board (Playing Piece will do that, too).

And that's that -- can you see how simple it really is? Now we'll just need to
go through all the details with a magnifying glass and we're done.

There are only two slightly tricky parts where the algorithms may not be
immediately obvious. The first part is in run-game function, where we need to
let the player and AI make their turns one after the other. Unlike most other
games, in Reversi there may be times when one side can't make a move but the
other can and the game continues until the first side can move again.

Therefore, we need to handle three situations: normal case where after my turn,
the turn is passed on to the other side; optional case when the other side can
make no move so I keep the turn to myself, and the case at the end of game when
neither player can make a move and we have to break the loop.

We don't know how many turns there will be so we have to run an 'infinite'
loop; we need to be able to change whose turn it is, so we have to have a
variable 'turn', set to either 'player' or 'computer'. Note that in the 2nd
case we don't need to do anything because turn variable simply keeps the same
value.  We have to handle the 1st case by checking if other side has moves and
changing turn variable, and if other side has no moves, we handle the 3rd case
by checking if we have no moves, either, and breaking the loop.

The code would be a little simpler if we first did both checks and then had
the if/else block; but in this case we have to consider the performance and
note that it's expensive to check if a side has moves or not, and we can not
'reuse' that check because after the other side makes its move, conditions have
changes and I need to do the check again. As you can see, if the other side has
moves, the check of my own moves would be wasted. With current logic, I only
run the second check if the second fails.

Another slightly tricky point is that checks run after a turn -- nothing is
done at the beginning. I rely on the fact that when the game begins, there is
always a valid move available, and after first turn there is a check for other
side's moves so that if turn goes to the other side, I know it can move.
Wouldn't it be clearer to run checks at the beginning of turn?

If we were to do that, the logic would be slightly more complicated: I have to
skip loop iteration if I have no moves and the other side does, and I have to
give turn to the other side at the end of loop without a check.

It's easier to handle all logic at the end of turn because I can handle all
cases in the same spot and we don't need to explicitly skip the turn because
I'm already at the end of it.




`timer.py <_static/timer.py>`_

.. literalinclude:: .static/timer.py

.. sourcecode:: sh

    $ ./timer.py
    0:25


`zfill(n)` string method will add zeroes to expand the string to `n` length.

`try: ... except KeyboardInterrupt:` construct will exit cleanly when you hit Ctrl-C to stop the timer.

`if __name__ == "__main__":` block will not run if this file is imported by another module, but will run otherwise. This is very useful to let other programs use functionality contained here without running the actual timer.

