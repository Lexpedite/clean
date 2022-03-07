# NAME TBD

## About

Akoma Ntoso is a markup language for legislative documents.

In the same way that Markdown is a plain-text markup language for generating
HTML, NAME TBD is a plain-text markup language for generating Akoma Ntoso
representations of statutes.

## Installation

TODO

## Usage

Write your markup, load it into a string variable, and run 

```python
from NAMETBD import generate_act

text = """Title

1. Section one.
"""

print(generate_act(text))
```

## Format

A NAMETBD formatted piece of legislation has the following features:

* The first line is the short title of the act.
* Headers are preceded by a blank line, and appear on their own line.
* Sections begin with a number, then a period, then a space, and their
  text.
* Subsections are indented, and begin with a number in parentheses
* Paragraphs are indnted, and begin with a letter in parenthesis
* Subparagraphs are indented, and begin with a lowercase roman numeral in parenthesis
* Text is kept on one line.

