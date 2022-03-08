import pytest
from ..clean import *

@pytest.mark.parametrize("good_paragraph_index",[
    "(aa)",
    "(ab.1)",
    "(aaa.1.2345)"
])
def test_parse_paragraph_index(good_paragraph_index):
    assert paragraph_index.parseString(good_paragraph_index,parse_all=True)

@pytest.mark.parametrize("bad_paragraph_index",[
    "(1a)",
    "<a>",
    "(a1)",
    "(aa",
    "a)",
    "(A)"
])
@pytest.mark.xfail
def test_parse_bad_paragraph_index(bad_paragraph_index):
    with pytest.raises(AttributeError):
        assert paragraph_index.parseString(bad_paragraph_index,parse_all=True)

def test_parse_paragraph_index_structure():
    assert paragraph_index.parseString("(a)",parse_all=True)['paragraph number'] == "a"

@pytest.mark.parametrize("good_insert_index",[
    ".1",
    ".1.2"
])
def test_parse_insert_index(good_insert_index):
    assert insert_index.parseString(good_insert_index,parse_all=True)


# test_target = section_index
# show_parse("1.")
# show_parse("1.2.")

### It is not possible to distinguish paragraph (i) from
### sub-paragraph (i) in the abstract, so it will need
### to depend on a larger structure.

### We also aren't distinguishing between well-formed and
### poorly-formed lower-case roman numbers.
# test_target = sub_paragraph_index

# show_parse("(iiiv.1.2234)")

# test_target = sub_section_index
# show_parse("(1.2)")

# test_target = heading
# show_parse("\nThis could be a heading.\n")

# test_target = sub_paragraph

# show_parse("(i) This is a subparagraph\n")

# test_target = sub_paragraph_list

# show_parse("""(i) subparagraph one
# (ii) subparagraph two""")

# test_target = paragraph

# show_parse("(a) This is a paragraph\n")
# # print(generate_paragraph(paragraph.parseString("(a) This is a paragraph\n", parse_all=True)))

# show_parse("""(a) this is a paragraph
#   (i) with a subparagraph, and
#   (ii) another subparagraph.
# """)

# test_target = sub_section

# show_parse("(1) This is a subsection.\n")

# show_parse("""(1) this is a subsection, with
#   (a) this as a paragraph, and
#     (i) with a subparagraph, and
#     (ii) another subparagraph, followed by
#   (b) another paragraph.
# """)

# test_target = section

# show_parse("1. This is a section.")

# show_parse("""1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs
#         (b) and another paragraph,
#     (2) and another subsection.
# """)

# show_parse("""
# Heading for Section
# 1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs
#         (b) and another paragraph,
#     (2) and another subsection.
# """)

# show_parse("""
# Heading for Section
# 1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs
#         (b) and another paragraph,

#     Heading for Sub-Section
#     (2) and another subsection.
# """)

# ## TODO: The header for the sub-section is not ending the above paragraph.

# test_target = title
# show_parse("Rock Paper Scissors Act\n")

# test_target = act
# show_parse("""Rock Paper Scissors Act

# 1. This is the text of the RPS Act,
#   (1) sub-section text.
# """)

# # Ultimately I want to be able to parse this.
# test = """
# Rock Paper Scissors Art

# Heading
# 1. This is the start of the section text.
#     (1) The section also has sub-sections
#         (a) with paragraphs.
#             (i) Which have sub-paragraphs

# No Main Section
# 2. (1) This is a section with no text and an immediate sub-section.

# Sandwiches
# 3. This is a section
#     (a) with direct paragraphs,
#     (b) like this,
#     and sandwich text.

# Multi-line Text
# 4. This is a section where the text continues
#     across more than one line, and should
#     all be treated as the same piece of text,
#     (1) followed by a subsection, which also
#         extends across more than one line.
# """

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