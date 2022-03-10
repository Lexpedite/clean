from ..clean import *

def test_readme_demo():
    file = open('tests/rps.clean')
    text = file.read()
    file.close()
    parse_result = act.parseString(addExplicitIndents(text),parse_all=True)
    an = generate_act(parse_result)
    assert an == """<?xml version="1.0" encoding="UTF-8"?><akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"><act><preface><p class="title"><shortTitle>Rock Paper Scissors Act</shortTitle></p></preface><body><section eId="sec_1"><num>1</num><heading>Players</heading><content><p>A game of rock paper scissors has two players.</p></content></section><section eId="sec_2"><num>2</num><intro><p>There are three signs:</p></intro><subSection eId="sec_2__subsec_1"><num>1</num><content><p>Rock,</p></content></subSection><subSection eId="sec_2__subsec_2"><num>2</num><content><p>Paper, and</p></content></subSection><subSection eId="sec_2__subsec_3"><num>3</num><content><p>Scissors.</p></content></subSection></section><section eId="sec_3"><num>3</num><heading>Defeating Relationships</heading><subSection eId="sec_3__subsec_1"><num>1</num><content><p>Rock beats Scissors,</p></content></subSection><subSection eId="sec_3__subsec_2"><num>2</num><content><p>Scissors beats Paper, and</p></content></subSection><subSection eId="sec_3__subsec_3"><num>3</num><content><p>Paper beats Rock.</p></content></subSection></section><section eId="sec_4"><num>4</num><heading>Winner</heading><content><p>The winner of a game is the player who throws a sign that beats the sign of the other player.</p></content></section></body></act></akomaNtoso>"""


# # print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n", parse_all=True)))
# print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n", parse_all=True)))
# print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n  (i) with a sub-paragraph,\n  (ii) and another sub-paragraph.\n", parse_all=True)))

# print(generate_sub_section(sub_section.parseString("""(1) this is a subsection, with
#   (a) this as a paragraph, and
#     (i) with a subparagraph, and
#     (ii) another subparagraph, followed by
#   (b) another paragraph.
# """, parse_all=True)))

# print(generate_section(section.parseString("""1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs
#         (b) and another paragraph,
#     (2) and another subsection.
# """, parse_all=True)))

# print(generate_section(section.parseString("""
# Heading for Section
# 1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs
#         (b) and another paragraph,
#     (2) and another subsection.
# """, parse_all=True)))

# print(generate_act(act.parseString("""Rock Paper Scissors Act
    
# 1. This is the text of the RPS Act,
#   (1) sub-section text.
# """, parse_all=True)))