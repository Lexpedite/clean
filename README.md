# Canadian Legal Enactments in Akoma Ntoso (CLEAN)

## About

[Akoma Ntoso](http://www.akomantoso.org/) is a markup language for 
legislative documents.

In the same way that Markdown is a plain-text markup language for generating
HTML, CLEAN is a plain-text markup language for generating Akoma Ntoso
representations of Canadian statutes and regulations.

## Installation

TODO

## Usage

Write your markup, load it into a string variable, and run 

```python
from clean import generate_act

text = """Title

1. Section one.
"""

print(generate_act(text))
```

## Format

A CLEAN-formatted piece of legislation has the following features:

* The first line is the short title of the act.
* Headers are preceded by a blank line, and appear on their own line.
* Sections begin with a number, then a period, then a space, and their
  text.
* Subsections are indented, and begin with a number in parentheses
* Paragraphs are indented again, and begin with a letter in parentheses
* Subparagraphs are indented thrice, and begin with a lowercase roman numeral in parentheses
* Text is kept on one line.

An example act might look like this:
```text
Rock Paper Scissors Act

Players
1. A game of rock paper scissors has two players.
2. There are three signs:
  (1) Rock,
  (2) Paper, and
  (3) Scissors.

Defeating Relationships
3. The signs have the following relationships:
  (1) Rock beats Scissors,
  (2) Scissors beats Paper, and
  (3) Paper beats Rock.

Winner
4. The winner of a game is the player who throws a sign that beats the sign of the other player.
```