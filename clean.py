# CLEAN - Canadian Legal Enactments in Akoma Ntoso
# This library includes a parser for CLEAN-formatted plain-text
# legal documents, and functions to generate Akoma Ntoso versions
# of the documents expressed in that language.

from pyparsing import *
import string

ParserElement.setDefaultWhitespaceChars(' \t')
# Define terms for parser
OPEN = "("
CLOSE = ")"
DOT = "."
SOL = line_start
NL = Suppress(Literal('\n'))
BLANK_LINE = SOL + NL
UP = SOL + Literal("INDENT")
DOWN = SOL + Literal("UNDENT")
lowercase_roman_numerals = ['i','v','x','l','c','d','m']

text_line = Combine(OneOrMore(Word(printables)),adjacent=False,join_string=" ")
# text_block = Combine(OneOrMore(text_line),adjacent=False,join_string=" ") + BLANK_LINE

# Parser elements for lowercase roman numerals
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

lowercase_roman_number = Word(lowercase_roman_numerals)

# Parser elements for CLEAN
number = Word(nums) 
insert_index = Forward()
insert_index <<= Group(Suppress(DOT) + number("insert number")) + Optional(insert_index)
paragraph_index = NL + Suppress(OPEN) + Word(string.ascii_lowercase, string.ascii_lowercase)('paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
section_index = NL + number("section number") + Optional(insert_index)('insert index') + Suppress(DOT)
sub_paragraph_index =  NL + Group(Suppress(OPEN) + lowercase_roman_number('sub-paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE))
sub_section_index = NL + Suppress(OPEN) + number('sub-section number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
sub_paragraph = Forward()
paragraph = Forward()
sub_section = Forward()
section = Forward()
numbered_part = sub_paragraph_index ^ paragraph_index ^ sub_section_index ^ section_index ^ DOWN ^ UP
legal_text = Combine(ZeroOrMore(NL ^ Word(printables), stop_on=numbered_part).set_debug(), adjacent=False, join_string=" ")
heading = BLANK_LINE + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('heading text')
title = lineStart + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('title text') + NL
sub_paragraph <<= sub_paragraph_index('sub-paragraph index') + legal_text('sub-paragraph text')
sub_paragraph_list = OneOrMore(Group(sub_paragraph))
paragraph <<= \
  paragraph_index('paragraph index') + \
  legal_text('paragraph text') + \
  Optional(
    (Suppress(UP) + \
    sub_paragraph_list + \
    Suppress(DOWN))('sub-paragraphs') + \
    Optional(legal_text('paragraph post'))
  )  
paragraph_list = OneOrMore(Group(paragraph))
sub_section <<= Optional(heading)('sub-section header') + sub_section_index('sub-section index') + legal_text('sub-section text') + Optional( \
    (Suppress(UP) + \
    paragraph_list + \
    Suppress(DOWN))('paragraphs') + \
    Optional(legal_text('sub-section post'))
    )
sub_section_list = OneOrMore(Group(sub_section))
empty_section = Optional(heading)('section header') + \
    section_index('section index') + \
    Suppress(UP) + \
    sub_section_list('sub-sections') + \
    Suppress(DOWN)
full_section = Optional(heading)('section header') + \
    section_index('section index') + \
    legal_text('section text') + \
    Optional( 
    (Suppress(UP) + \
    (sub_section_list('sub-sections') ^ paragraph_list('paragraphs')) + \
    Suppress(DOWN)) + \
    Optional(legal_text('section post'))
    )
section <<= full_section ^ empty_section
# Only for sections, the initial text is optional. if it is missing,
# there can be no post text.
act = title('title') + ZeroOrMore(Group(section))('body')


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
    for sp in subparagraphs_list:
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
    for p in node['paragraphs']:
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
    if 'section text' in node:
      output += "<intro><p>"
      output += node['section text']
      output += "</p></intro>"
    for p in node['sub-sections']:
      output += generate_sub_section(p, prefix)
  else:
    if 'section text' in node:
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

def generate_akn(text):
  return generate_act(act.parseString(addExplicitIndents(text)))

import sys
if __name__ == '__main__':
  file = open(sys.argv[1])
  text = file.read()
  file.close()
  parsed = act.parseString(text,parse_all=True)
  print(generate_act(parsed))

def addExplicitIndents(string):
  """A function to add explicit indents to a text file for block-based encodings,
  because most of the indent features of PyParsing don't work properly."""

  UP = "INDENT\n"
  DOWN = "UNDENT\n"

  levels = [0]
  output = ""

  for line in string.splitlines():
    level = len(line) - len(line.lstrip(' '))
    if level == levels[-1]: # The level has not changed
      output += line + '\n'
    elif level > levels[-1]: # The indent has increased
      levels.append(level)
      output += UP
      output += line + '\n'
    elif level < levels[-1]: # The indent has gone down
      if level in levels: #We are returning to a previous level
        while level != levels[-1]:
          output += DOWN
          levels.pop()
        output += line + '\n'
      else:
        raise Exception("Unindent to a level not previously used in " + line)
  # At this point, it is possible that we have a high indentation level,
  # and we need to add UNDENTS to close out the blocks
  while len(levels) > 1:
    output += DOWN
    levels.pop()
  return output
