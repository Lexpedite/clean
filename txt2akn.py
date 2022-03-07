# A parser for the txt2akn language, which is designed to allow the user to generate
# minimal and consistent Akoma Ntoso documents from an easy-to-use plain text format.

from pprint import pprint
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
EOL = LineEnd().suppress()
BLANK_LINE = Suppress(line_start) + EOL

lowercase_roman_numerals = ['i','v','x','l','c','d','m']

rn_thousands = ZeroOrMore(Literal('m'))
rn_hundreds_cm = Literal('c') + Literal('m')
rn_hundreds_c = Literal('c') * (0,3)
rn_hundreds_cd = Literal('c') + Literal('d')
rn_hundreds_d = Literal('d')
rn_hundreds = rn_hundreds_cm ^ rn_hundreds_c ^ rn_hundreds_cd ^ rn_hundreds_d
rn_tens_x = Literal('x') * (0,3)
rn_tens_xc = Literal('x') + Literal('c')
rn_tens_xd = Literal('x') + Literal('d')
rn_tens_d = Literal('d') + rn_tens_x
rn_tens = rn_tens_x ^ rn_tens_xc ^ rn_tens_xd ^ rn_tens_d
rn_ones_i = Literal('i') * (0,3)
rn_ones_iv = Literal('i') + Literal('v')
rn_ones_v = Literal('v') + rn_ones_i 
rn_ones_ix = Literal('i') + Literal('x')
rn_ones = rn_ones_i ^ rn_ones_iv ^ rn_ones_v ^ rn_ones_ix
rn = rn_thousands + rn_hundreds + rn_tens + rn_ones

# TODO: I don't know if the rn parse element will accept a blank string,
# and it hasn't been tested.

lowercase_roman_number = Word(lowercase_roman_numerals)
number = Word(nums)
insert_index = Forward()
insert_index <<= Group(Suppress(DOT) + number("insert number")) + Optional(insert_index)
paragraph_index = Suppress(OPEN) + Word(string.ascii_lowercase, string.ascii_lowercase)('paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
section_index = number("section number") + Optional(insert_index)('insert index') + Suppress(DOT)
sub_paragraph_index = Group(Suppress(OPEN) + lowercase_roman_number('sub-paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE) )
sub_section_index = Suppress(OPEN) + number('sub-section number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
sub_paragraph = Forward()
paragraph = Forward()
sub_section = Forward()
section = Forward()
numbered_part = sub_paragraph_index ^ paragraph_index ^ sub_section_index ^ section_index ^ BLANK_LINE
heading = EOL + lineStart + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('heading text') + EOL
title = lineStart + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('title text') + EOL
sub_paragraph <<= sub_paragraph_index('sub-paragraph index') + Combine(ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('sub-paragraph text') + EOL
sub_paragraph_list = OneOrMore(Group(sub_paragraph))
paragraph <<= paragraph_index + Combine(ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('paragraph text') + EOL + Optional(IndentedBlock(sub_paragraph_list))('sub-paragraphs')
paragraph_list = OneOrMore(Group(paragraph))
sub_section <<= Optional(heading)('sub-section header') + sub_section_index('sub-section index') + Combine(ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('sub-section text') + EOL + Optional(IndentedBlock(paragraph_list))('paragraphs')
sub_section_list = OneOrMore(Group(sub_section))
section <<= Optional(heading)('section header') + section_index('section index') + Combine(ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('section text') + EOL + Optional(IndentedBlock(sub_section_list)('sub-sections'))
act = title('title') + ZeroOrMore(Group(section))('body')

test_target = number

def show_parse(string):
  print("\n\n")
  print(test_target.parseString(string, parse_all=True).dump())

def generate_sub_paragraph(node, prefix=""):
  eId = prefix + "__subpara_" + node['sub-paragraph index']['sub-paragraph number']
  output = "<subParagraph eId=\"" + eId + "\"><num>"
  output += node['sub-paragraph index']['sub-paragraph number']
  output += "</num><content><p>"
  output += node['sub-paragraph text']
  output += "</p></content></subParagraph>"
  return output

def generate_paragraph(node, prefix=""):
  p_prefix = prefix + "__para_" + node['paragraph number']
  output = "<paragraph eId=\"" + p_prefix + "\"><num>"
  output += node['paragraph number']
  output += "</num>"
  if 'sub-paragraphs' in node:
    output += "<intro><p>"
    output += node['paragraph text']
    output += "</p></intro>"
    subparagraphs_list = node['sub-paragraphs']
    for sp in subparagraphs_list[0]:
      # output += generate_sub_paragraph(sp)
      output += generate_sub_paragraph(sp, p_prefix)
  else:
    output += "<content><p>"
    output += node['paragraph text']
    output += "</p></content>"
  output += "</paragraph>"
  return output

def generate_sub_section(node, prefix=""):
  ss_prefix = prefix + "__subsec_" + node['sub-section number']
  output = "<subSection eId=\"" + ss_prefix + "\"><num>"
  output += node['sub-section number']
  output += "</num>"
  if 'paragraphs' in node:
    output += "<intro><p>"
    output += node['sub-section text']
    output += "</p></intro>"
    for p in node['paragraphs'][0]:
      output += generate_paragraph(p, ss_prefix)
  else:
    output += "<content><p>"
    output += node['sub-section text']
    output += "</p></content>"
  output += "</subSection>"
  return output

def generate_section(node):
  prefix = "sec_" + node['section number']
  output = "<section eId=\"" + prefix + "\"><num>"
  output += node['section number']
  output += "</num>"
  if 'heading text' in node:
    output += "<heading>"
    output += node['heading text']
    output += "</heading>"
  if 'sub-sections' in node:
    output += "<intro><p>"
    output += node['section text']
    output += "</p></intro>"
    for p in node['sub-sections'][0]:
      output += generate_sub_section(p, prefix)
  else:
    output += "<content><p>"
    output += node['section text']
    output += "</p></content>"
  output += "</section>"
  return output

def generate_title(node):
  output = '<preface><p class="title"><shortTitle>'
  output += node['title text']
  output += "</shortTitle></p></preface>"
  return output

def generate_act(node):
  output = '<?xml version="1.0" encoding="UTF-8"?><akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"><act>'
  if 'title' in node:
    output += generate_title(node)
  if 'body' in node:
    output += "<body>"
    for sec in node['body']:
      output += generate_section(sec)
    output += "</body>"
  output += "</act></akomaNtoso>"
  return output


test_target = paragraph_index

show_parse("(aa)")

show_parse("(ab.1)")

show_parse("(aaa.1.2234)")

test_target = insert_index

show_parse(".1")
show_parse(".1.2")

test_target = section_index
show_parse("1.")
show_parse("1.2.")

# # It is not possible to distinguish paragraph (i) from
# # sub-paragraph (i) in the abstract, so it will need
# # to depend on a larger structure.

# # We also aren't distinguishing between well-formed and
# # poorly-formed lower-case roman numbers.

test_target = sub_paragraph_index

show_parse("(iiiv.1.2234)")

test_target = sub_section_index
show_parse("(1.2)")

test_target = heading
show_parse("\nThis could be a heading.\n")

test_target = sub_paragraph

show_parse("(i) This is a subparagraph\n")

test_target = sub_paragraph_list

show_parse("""(i) subparagraph one
(ii) subparagraph two""")

test_target = paragraph

show_parse("(a) This is a paragraph\n")
# print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n", parse_all=True)))

show_parse("""(a) this is a paragraph
  (i) with a subparagraph, and
  (ii) another subparagraph.
""")

test_target = sub_section

show_parse("(1) This is a subsection.\n")

show_parse("""(1) this is a subsection, with
  (a) this as a paragraph, and
    (i) with a subparagraph, and
    (ii) another subparagraph, followed by
  (b) another paragraph.
""")

test_target = section

show_parse("1. This is a section.")

show_parse("""1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""")

show_parse("""
Heading for Section
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""")

show_parse("""
Heading for Section
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,

    Heading for Sub-Section
    (2) and another subsection.
""")

## TODO: The header for the sub-section is not ending the above paragraph.

test_target = title
show_parse("Rock Paper Scissors Act\n")

test_target = act
show_parse("""Rock Paper Scissors Act

1. This is the text of the RPS Act,
  (1) sub-section text.
""")


# Ultimately I want to be able to parse this.
test = """
Rock Paper Scissors Art

Heading
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs

No Main Section
2. (1) This is a section with no text and an immediate sub-section.

Sandwiches
3. This is a section
    (a) with direct paragraphs,
    (b) like this,
    and sandwich text.

Multi-line Text
4. This is a section where the text continues
    across more than one line, and should
    all be treated as the same piece of text,
    (1) followed by a subsection, which also
        extends across more than one line.
"""

print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n", parse_all=True)))
print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n  (i) with a sub-paragraph,\n  (ii) and another sub-paragraph.\n", parse_all=True)))

print(generate_sub_section(sub_section.parseString("""(1) this is a subsection, with
  (a) this as a paragraph, and
    (i) with a subparagraph, and
    (ii) another subparagraph, followed by
  (b) another paragraph.
""", parse_all=True)))

print(generate_section(section.parseString("""1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""", parse_all=True)))


print(generate_section(section.parseString("""
Heading for Section
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""", parse_all=True)))

print(generate_act(act.parseString("""Rock Paper Scissors Act

1. This is the text of the RPS Act,
  (1) sub-section text.
""", parse_all=True)))