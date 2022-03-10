import pytest
from ..clean import addExplicitIndents

def test_indents():
    text = """Rock Paper Scissors Act

Players
1. A game of rock paper scissors has two players.
2. There are three signs:
  (1) Rock,
  (2) Paper, and
  (3) Scissors.

Defeating Relationships
3.
  (1) Rock beats Scissors,
  (2) Scissors beats Paper, and
  (3) Paper beats Rock.

Winner
4. The winner of a game is the player who throws
a sign that beats the sign of the other player.
"""
    indents = addExplicitIndents(text)
    assert indents == """Rock Paper Scissors Act

Players
1. A game of rock paper scissors has two players.
2. There are three signs:
INDENT
  (1) Rock,
  (2) Paper, and
  (3) Scissors.
UNDENT

Defeating Relationships
3.
INDENT
  (1) Rock beats Scissors,
  (2) Scissors beats Paper, and
  (3) Paper beats Rock.
UNDENT

Winner
4. The winner of a game is the player who throws
a sign that beats the sign of the other player.
"""

def test_multi_level_indents():
    text = """
1.
    1.1
        1.1.1
        1.1.2
    1.2
        1.2.1
    1.3
2.
    2.1
3.
    3.1
        3.1.1
        3.1.2
4.
"""
    indents = addExplicitIndents(text)
    assert indents == """
1.
INDENT
    1.1
INDENT
        1.1.1
        1.1.2
UNDENT
    1.2
INDENT
        1.2.1
UNDENT
    1.3
UNDENT
2.
INDENT
    2.1
UNDENT
3.
INDENT
    3.1
INDENT
        3.1.1
        3.1.2
UNDENT
UNDENT
4.
"""