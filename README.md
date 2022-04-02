# Canadian Legal Enactments in Akoma Ntoso (CLEAN)

## About

[Akoma Ntoso](http://www.akomantoso.org/) is a markup language for 
legislative documents.

In the same way that Markdown is a plain-text markup language for generating
HTML, CLEAN is a plain-text markup language for generating Akoma Ntoso
representations of Canadian statutes and regulations.

## Installation

`pip install clean-law`

## Usage

Write your markup, load it into a string variable, and run 

```python
from clean.clean import generate_akn

text = """Title

1. Section one."""

print(generate_akn(text))

# <?xml version="1.0" encoding="UTF-8"?><akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"><act><preface><p class="title"><shortTitle>Title</shortTitle></p></preface><body><section eId="sec_1"><num>1</num><content><p>Section one.</p></content></section></body></act></akomaNtoso>
```

## Format

A CLEAN-formatted piece of legislation has the following features:

### Title

The title of the act is the first line of the file.

### Headers

Sections and Sub-Sections can have headers, which is a single line of text
immediately above the section or subsection, preceded by a blank line.

It is necessary to precede headers with a blank line in order to distinguish
them from sandwich text, described below.

### Insert Indexes

When making amendments to legislation, we want to be able to insert parts
without changing the numbering of the existing parts, at least until there
is a revision of the statute book. This is accomplished by using insert
indexes, which are always a period, followed by a number, which increases
sequentially.

If you want to insert a new section between two existing inserted sections,
the insert indexes can nest, as follows:

```text
1.
  (1)
  (1.1) - first inserted sub-section. 
  (1.1.1) - third inserted sub-section.
  (1.2) - second inserted sub-section
  (2)
```

For all of the index types, sections, sub-sections, paragraphs, and
sub-paragraphs, the insert indexes appear to the right of the index
number, and before any closing punctuation, as follows:

```text
1.1.
  (1.1)
    (a.1)
      (i.1)
```

### Sections

Sections are indicated by a section index which is an arabic number followed
by a period.

A section may have a header.

A section index may be followed by the text of the section. If it is, it may
also have an indented list of sub-sections, or paragraphs (but not both). If
It has an indented list of sub-sections or paragraphs, it can also have
"sandwich text" at the bottom.

Here are some valid sections:

```text
1. This is a section.
2. This is a section with
  (1) a subsection.

Section Three
3. This is a section with a header, and
  (a) paragraphs
and sandwich text.
3.1 As with all text, it
can be spread across multiple lines.
```

Note that you can use indexes, such as in a cross-reference, 
inside the text of a section, but only if the index does not
appear at the start of a line.

```text
1. If you want to refer to sub-section (2), this
will work just fine.

2. If you want to refer to sub-section
(1) this will not work.
```
### Sub-Sections

Sub-sections are indicated with an index of an arabic number in parentheses.
They must be indented from their parent section. They can have a header,
which also must be indented the same amount. They must be followed by legal
text, and may also then have an indented list of paragraphs. If there is an
indented list of paragraphs, it may be followed by sandwich text.

Legal text can go across multiple lines, but if they appear at the start
of a line, that will cause confusion.

```text
1. This is a section.
  (1) This is the first sub-section.
    (a) the first subsection has paragraphs.
  with sandwich text.

  Named Sub-Subection
  (2) This is a subsection with a header, and
  which refers to subsection (1) in a way
  that works. 
```

### Paragraphs

Paragraphs are indented from a section or sub-section, and are indicated
with a lower-case alphabetic character or characters surrounded by 
parenthesis. They must then have legal text, which can span across lines
in the same way as in sections and sub-sections. A paragraph can have
an indented list of sub-paragraphs. Paragraphs cannot have a header.

### Sub-Paragraphs

Sub-paragraphs are indented from a paragraph, and are indicated wth a
lower-case roman numeral surrounded in parentheses. They must have
legal text, which can span across lines in the usual way.
Sub-paragraphs cannot have further sub-divisions, and cannot have a header.

### Spans

Akoma Ntoso provides a mechanism for you to identify 
a sub-part of a block of text inside a law. In CLEAN you can create
these named spans by using the following syntax: `[name]{contents}`.

```text
1. This is an example of the text of a section [name]{with
a named span of text} included in it.
```

The name given to a span between the square brackets must not have any
spaces in it. It should be unique to be useful. Spans can be 
nested inside one another.

## An Example

An example act might look like this:
```text
Rock Paper Scissors Act

Players
1. A game of rock paper scissors has two players.
2. There are three signs:
  (a) Rock,
  (b) Paper, and
  (c) Scissors.

Defeating Relationships
3.
  (1) Rock beats Scissors,
  (2) Scissors beats Paper, and
  (3) Paper beats Rock.

Winner
4. The winner of a game is the player who throws
a sign that beats the sign of the other player.
```

## Known Issues
Some things to be aware of if you are playing with it:
* there is no validation of roman numerals. If it uses `i`, `v`, `x`, etc., it
  will be accepted

