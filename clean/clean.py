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
NL = Suppress(Literal('\n'))
BLANK_LINE = line_start + NL
UP = NL + "INDENT"
DOWN = NL + "UNDENT"
SPANNAME_START = Suppress("[")
SPANNAME_STOP = Suppress("]")
SPAN_START = Suppress("{")
SPAN_STOP = Suppress("}")
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
paragraph_index = NL + Suppress(OPEN) + original_text_for(Word(string.ascii_lowercase)('paragraph number') + Optional(insert_index)('insert index')) + Suppress(CLOSE)
section_index = NL + original_text_for(number("section number") + Optional(insert_index)('insert index')) + Suppress(DOT)
sub_paragraph_index =  NL + Suppress(OPEN) + original_text_for(lowercase_roman_number('sub-paragraph number') + Optional(insert_index)('insert index')) + Suppress(CLOSE)
sub_section_index = NL + Suppress(OPEN) + original_text_for(number('sub-section number') + Optional(insert_index)('insert index')) + Suppress(CLOSE)
sub_paragraph = Forward()
paragraph = Forward()
sub_section = Forward()
section = Forward()
numbered_part = sub_paragraph_index ^ paragraph_index ^ sub_section_index ^ section_index ^ DOWN ^ UP ^ BLANK_LINE
span_name = SPANNAME_START + Word(alphanums) + SPANNAME_STOP
span = Forward()
span <<= Group(Opt(NL) + span_name)('span name') + SPAN_START + Group(ZeroOrMore(Group(span) ^ Combine(OneOrMore((Opt(NL) + Word(printables,exclude_chars="[}"))),join_string=" ",adjacent=False)))('span body') + SPAN_STOP
# legal_text = Combine(ZeroOrMore( span ^ NL ^ Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")
legal_text = \
  ZeroOrMore( \
    Group(span) \
    ^ \
    Combine(\
      OneOrMore(\
        (Opt(NL) + Word(printables)),
        stop_on=span ^ numbered_part\
      ), 
      adjacent=False, 
      join_string=" "\
    ),
    stop_on=numbered_part\
  )
# legal_text.set_whitespace_chars(' \t')
heading = NL + NL + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('heading text')
title = lineStart + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('title text')
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
act = title('title') + (FollowedBy(heading) | NL) + ZeroOrMore(Group(section))('body') + ZeroOrMore(NL)

def generate_span(node, prefix=""):
  output = ' <span eId="' + prefix + ("." if prefix else "") + node['span name'][0] + '">'
  output += generate_legal_text(node['span body'],prefix + node['span name'][0])
  output += "</span> "
  return output

def generate_legal_text(node, prefix=""):
  output = ""
  for element in node:
    if type(element) == str:
      output += element
    else: # the only other option is a span
      output += generate_span(element,prefix)
  return output

def generate_sub_paragraph(node, prefix=""):
  eId = prefix + "__subpara_" + node['sub-paragraph index'][0].replace('.','_')
  output = "<subParagraph eId=\"" + eId + "\"><num>"
  output += node['sub-paragraph index'][0]
  output += "</num><content><p>"
  output += generate_legal_text(node['sub-paragraph text'],eId)
  output += "</p></content></subParagraph>"
  return output

def generate_paragraph(node, prefix=""):
  p_prefix = prefix + "__para_" + node['paragraph index'][0].replace('.','_')
  output = "<paragraph eId=\"" + p_prefix + "\"><num>"
  output += node['paragraph index'][0]
  output += "</num>"
  if 'sub-paragraphs' in node and len(node['sub-paragraphs']):
    output += "<intro><p>"
    output += generate_legal_text(node['paragraph text'], p_prefix)
    output += "</p></intro>"
    subparagraphs_list = node['sub-paragraphs']
    for sp in subparagraphs_list:
      output += generate_sub_paragraph(sp, p_prefix)
      if len(node['paragraph post']):
        output += "<wrapup><p>"
        output += generate_legal_text(node['paragraph post'], p_prefix)
        output += "</p></wrapup>"
  else:
    output += "<content><p>"
    output += generate_legal_text(node['paragraph text'],p_prefix)
    output += "</p></content>"
  output += "</paragraph>"
  return output

def generate_sub_section(node, prefix=""):
  ss_prefix = prefix + "__subsec_" + node['sub-section index'][0].replace('.','_')
  output = "<subSection eId=\"" + ss_prefix + "\"><num>"
  output += node['sub-section index'][0]
  output += "</num>"
  if 'heading text' in node and len(node['heading text']):
    output += "<heading>"
    output += node['heading text']
    output += "</heading>"
  if 'paragraphs' in node and len(node['paragraphs']):
    output += "<intro><p>"
    output += generate_legal_text(node['sub-section text'], ss_prefix)
    output += "</p></intro>"
    for p in node['paragraphs']:
      output += generate_paragraph(p, ss_prefix)
    if len(node['sub-section post']):
      output += "<wrapup><p>"
      output += generate_legal_text(node['sub-section post'], ss_prefix)
      output += "</p></wrapup>"
  else:
    output += "<content><p>"
    output += generate_legal_text(node['sub-section text'], ss_prefix)
    output += "</p></content>"
  output += "</subSection>"
  return output

def generate_section(node):
  prefix = "sec_" + node['section index'][0].replace('.','_')
  output = "<section eId=\"" + prefix + "\"><num>"
  output += node['section index'][0]
  output += "</num>"
  if 'heading text' in node and len(node['heading text']):
    output += "<heading>"
    output += node['heading text']
    output += "</heading>"
  if 'sub-sections' in node or 'paragraphs' in node:
    if len(node['section text']):
      output += "<intro><p>"
      output += generate_legal_text(node['section text'], prefix)
      output += "</p></intro>"
    if 'sub-sections' in node and len(node['sub-sections']):
      for p in node['sub-sections']:
        output += generate_sub_section(p, prefix)
    elif len(node['paragraphs']):
      for p in node['paragraphs']:
        output += generate_paragraph(p, prefix)
    if len(node['section post']):
      output += "<wrapup><p>"
      output += generate_legal_text(node['section post'], prefix)
      output += "</p></wrapup>"
  else:
    if len(node['section text']):
      output += "<content><p>"
      output += generate_legal_text(node['section text'], prefix)
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
  # Ideally, we would strip blank lines off the end of the indented file.
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
      output += line.lstrip(' ') + '\n'
    elif level > levels[-1]: # The indent has increased
      levels.append(level)
      output += UP
      output += line.lstrip(' ') + '\n'
    elif level < levels[-1]: # The indent has gone down
      if level in levels: #We are returning to a previous level
        while level != levels[-1]:
          output += DOWN
          levels.pop()
        output += line.lstrip(' ') + '\n'
      else:
        raise Exception("Unindent to a level not previously used in " + line)
  # At this point, it is possible that we have a high indentation level,
  # and we need to add UNDENTS to close out the blocks
  while len(levels) > 1:
    output += DOWN
    levels.pop()
  while output.splitlines()[-1] == "\n":
    output.pop()
  return output
