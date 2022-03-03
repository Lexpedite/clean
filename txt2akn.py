# A parser for the txt2akn language, which is designed to allow the user to generate
# minimal and consistent Akoma Ntoso documents from an easy-to-use plain text format.

from tokenize import Number
from pyparsing import *
import string

# An Act Is a title, followed by a body.
# A title is text
# A body is a group of hierarchical elements
# A hierarchical element is an optional hierarchical element type,
# an optional number, and an optional header followed by an
# optional intro, then a list of hierarchical components or content, and
# an optional wrapup. But the wrapup only exists if there was an intro.
# An element type is Part, Division, Chapter, etc.
# A number is a dotted number or a bracketed number.
# a dotted number is numerals, optional letters, and a period.
# a brackedet number is a bracket, a numeral or index, and a closed bracket.

# 1.1. a.1 aa.11.1

OPEN = "("
CLOSE = ")"
DOT = "."

lowercase_roman_numerals = ['i','v','x','l','c','d','m']
lowercase_roman_number = Word(lowercase_roman_numerals)
number = Word(nums)
insert_index = OneOrMore(Group(DOT + number))("insert index")
paragraph_index = Group(OPEN + Word(string.ascii_lowercase, string.ascii_lowercase)('paragraph number') + Optional(insert_index) + CLOSE )('paragraph index')
section_index = number("section number") + Optional(insert_index) + DOT
sub_paragraph_index = Group(OPEN + lowercase_roman_number('sub-paragraph number') + Optional(insert_index) + CLOSE )('sub-paragraph index')


test = "(aa)"
parse = paragraph_index.parseString(test, parse_all=True)
print(parse.asDict())

test = ".1"
parse = insert_index.parseString(test, parse_all=True)
print(parse.asDict())

test = "(ab.1)"
parse = paragraph_index.parseString(test, parse_all=True)
print(parse.asDict())

test = ".1.2"
parse = insert_index.parseString(test,parse_all=True)
print(parse.asDict())

test = "(aaa.1.2234)"
parse = paragraph_index.parseString(test, parse_all=True)
print(parse.asDict())

test = "1."
parse = section_index.parseString(test, parse_all=True)
print(parse.asDict())

test = "1.2."
parse = section_index.parseString(test, parse_all=True)
print(parse.asDict())

# It is not possible to distinguish paragraph (i) from
# sub-paragraph (i) in the abstract, so it will need
# to depend on a larger structure.

# We also aren't distinguishing between well-formed and
# poorly-formed lower-case roman numbers.
test = "(iiiv.1.2234)"
parse = sub_paragraph_index.parseString(test, parse_all=True)
print(parse.asDict())


"""
Rock Paper Scissors Art

Part 1 - The Rules

Heading
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
"""