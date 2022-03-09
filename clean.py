# CLEAN - Canadian Legal Enactments in Akoma Ntoso
# This library includes a parser for CLEAN-formatted plain-text
# legal documents, and functions to generate Akoma Ntoso versions
# of the documents expressed in that language.

# TODO: Headers are showing up as part of the previous text.
# TODO: Deal with sandwich sections.
# TODO: Make it possible to have empty sections.
# TODO: Get the AN Generator to use insert indexes.

from pyparsing import *
import string

ParserElement.setDefaultWhitespaceChars(' \t')
# Define terms for parser
OPEN = "("
CLOSE = ")"
DOT = "."
SOL = Suppress(line_start)
NL = Suppress(Literal('\n'))
BLANK_LINE = SOL + NL
lowercase_roman_numerals = ['i','v','x','l','c','d','m']

text_line = Combine(OneOrMore(Word(printables)),adjacent=False,join_string=" ") + NL
text_block = Combine(OneOrMore(text_line),adjacent=False,join_string=" ") + BLANK_LINE

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
paragraph_index = Suppress(OPEN) + Word(string.ascii_lowercase, string.ascii_lowercase)('paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
section_index = number("section number") + Optional(insert_index)('insert index') + Suppress(DOT)
sub_paragraph_index = Group(Suppress(OPEN) + lowercase_roman_number('sub-paragraph number') + Optional(insert_index)('insert index') + Suppress(CLOSE) )
sub_section_index = Suppress(OPEN) + number('sub-section number') + Optional(insert_index)('insert index') + Suppress(CLOSE)
sub_paragraph = Forward()
paragraph = Forward()
sub_section = Forward()
section = Forward()
numbered_part = sub_paragraph_index ^ paragraph_index ^ sub_section_index ^ section_index
heading = Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('heading text') + NL
title = lineStart + Combine(Word(string.ascii_uppercase, printables) + ZeroOrMore(Word(printables), stop_on=numbered_part), adjacent=False, join_string=" ")('title text') + NL + BLANK_LINE
sub_paragraph <<= sub_paragraph_index('sub-paragraph index') + Combine(ZeroOrMore(text_line, stop_on=numbered_part), adjacent=False, join_string=" ")('sub-paragraph text')
sub_paragraph_list = OneOrMore(Group(sub_paragraph))
paragraph <<= paragraph_index('paragraph index') + Combine(ZeroOrMore(text_line, stop_on=numbered_part), adjacent=False, join_string=" ")('paragraph text') + Optional(IndentedBlock(sub_paragraph_list,grouped=False))('sub-paragraphs')
paragraph_list = OneOrMore(Group(paragraph))
sub_section <<= Optional(heading)('sub-section header') + sub_section_index('sub-section index') + Combine(ZeroOrMore(text_line, stop_on=numbered_part), adjacent=False, join_string=" ")('sub-section text') + Optional(IndentedBlock(paragraph_list,grouped=False))('paragraphs')
sub_section_list = OneOrMore(Group(sub_section))
section <<= Optional(heading)('section header') + \
    section_index('section index') + \
    Combine(
      ZeroOrMore(
        text_line, 
        stop_on=numbered_part
      ), 
      adjacent=False, 
      join_string=" "
    )('section text') + \
    Optional(
      IndentedBlock(
        sub_section_list,
        grouped=False
      )('sub-sections')
    )
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
    output += "<intro><p>"
    output += node['section text']
    output += "</p></intro>"
    for p in node['sub-sections']:
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

import sys
if __name__ == '__main__':
  file = open(sys.argv[1])
  text = file.read()
  file.close()
  parsed = act.parseString(text,parse_all=True)
  print(generate_act(parsed))
