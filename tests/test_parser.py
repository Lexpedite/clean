import pytest
from ..clean import *

# Insert Indexes are used to add sections to a text between amendments,
# so as to avoid the need to renumber items and break cross-references.

class TestInsertIndex:

    @pytest.mark.parametrize("good_insert_index",[
        ".1",
        ".1.2"
    ])
    def test_parse_insert_index(self, good_insert_index):
        assert insert_index.parseString(good_insert_index,parse_all=True)

class TestSubParagraph:
    @pytest.mark.parametrize("good_subparagraph_index",[
        "(viii)",
        "(c)",
        "(i.123.4)",
        "(iv.5)"
    ])
    def test_parse_subpara_index(self, good_subparagraph_index):
        assert sub_paragraph_index.parseString(good_subparagraph_index,parse_all=True)

    @pytest.mark.parametrize("bad_subparagraph_index",[
        "(b)", #Must be roman numerals
        "(M)", # must be lower-case
        "(iivivi)", # TODO: must be well-formed roman numeral
    ])
    def test_parse_bad_subpara_index(self, bad_subparagraph_index):
        with pytest.raises(ParseException):
            assert sub_paragraph_index.parseString(bad_subparagraph_index,parse_all=True)

    def test_parse_subpara(self):
        parse = sub_paragraph.parseString("(i) Sub-paragraph here\n",parse_all=True) 
        assert parse

    def test_parse_multiline_subpara(self):
        parse = sub_paragraph.parseString("(i) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_parse_multiline_subpara_stop_new(self):
        parse = sub_paragraph.parseString("(i) This is the start\nand this is the rest\n(ii) Test ignore")
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_parse_multiline_subpara_stop_para(self):
        parse = sub_paragraph.parseString("(i) This is the start\nand this is the rest\n(b) test ignore")
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_subpara_structure(self):
        parse = sub_paragraph.parseString("(i) Sub-paragraph here\n",parse_all=True)
        dictionary = parse.asDict()
        assert dictionary == \
            {
                'sub-paragraph index': {
                    'sub-paragraph number': "i"
                },
                'sub-paragraph text': "Sub-paragraph here"
            }

    def test_parse_subparalist(self):
        parse = sub_paragraph_list.parseString("""(i) subparagraph one
    (ii) subparagraph two\n""",parse_all=True)
        assert parse

    
    def test_subparalist_structure(self):
        parse = sub_paragraph_list.parseString("""(i) subparagraph one
    (ii) subparagraph two\n""",parse_all=True)
        assert len(parse) == 2
        assert parse[0].asDict() == \
                {
                    'sub-paragraph index': {
                        'sub-paragraph number': "i"
                    },
                    'sub-paragraph text': "subparagraph one"
                }
        assert parse[1].asDict() == \
                {
                    'sub-paragraph index': {
                        'sub-paragraph number': "ii"
                    },
                    'sub-paragraph text': "subparagraph two"
                }

class TestParagraph:
    @pytest.mark.parametrize("good_paragraph_index",[
        "(aa)",
        "(ab.1)",
        "(aaa.1.2345)"
    ])
    def test_parse_paragraph_index(self, good_paragraph_index):
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
    def test_parse_bad_paragraph_index(self, bad_paragraph_index):
        with pytest.raises(ParseException):
            assert paragraph_index.parseString(bad_paragraph_index,parse_all=True)

    def test_parse_paragraph_index_structure(self):
        assert paragraph_index.parseString("(a)",parse_all=True)['paragraph number'] == "a"

    def test_parse_paragraph(self):
        assert paragraph.parseString("(a) This is paragraph.\n",parse_all=True)

    def test_parse_paragraph_with_subs(self):
        assert paragraph.parseString("""(a) this is a paragraph
    (i) with a subparagraph, and
    (ii) another subparagraph.
    """,parse_all=True)

    def test_parse_sandwich_paragraph(self):
        parse = paragraph.parseString("(a) This is the intro\n  (i) this is the sub-para, and\nthere is concluding sandwich text.\n",parse_all=True)
        assert parse.asDict()['sub-paragraphs'][0]['sub-paragraph text'] == "this is the sub-para, and"

    def test_parse_multiline_paragraph(self):
        parse = paragraph.parseString("(a) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['paragraph text'] == "This is the start and this is the rest"


class TestSubSection:
    @pytest.mark.parametrize("good_sub_section_index",[
        "(12)",
        "(4.1)",
        "(234.1.2345)"
    ])
    def test_parse_sub_section_index(self, good_sub_section_index):
        assert sub_section_index.parseString(good_sub_section_index,parse_all=True)

    @pytest.mark.parametrize("bad_sub_section_index",[
        "(12a)",
        "(4.1",
        "234.1.2345)",
        "(x)"
    ])
    @pytest.mark.xfail
    def test_parse_bad_sub_section_index(self, bad_sub_section_index):
        with pytest.raises(ParseException):
            assert sub_section_index.parseString(bad_sub_section_index,parse_all=True)

    def test_parse_subsection(self):
        assert sub_section.parseString("(1) This is a subsection.\n",parse_all=True)

    def test_parse_subsection_with_paras(self):
        assert sub_section.parseString("""(1) this is a subsection, with
    (a) this as a paragraph, and
        (i) with a subparagraph, and
        (ii) another subparagraph, followed by
    (b) another paragraph.
    """, parse_all=True)

    def test_parse_multiline_subsection(self):
        parse = sub_section.parseString("(1) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['sub-section text'] == "This is the start and this is the rest"


class TestSection:
    
    @pytest.mark.parametrize("good_section_index",[
        "1.",
        "12345.",
        "1.2."
    ])
    def test_parse_section_index(self, good_section_index):
        assert section_index.parseString(good_section_index,parse_all=True)

    @pytest.mark.parametrize("bad_section_index",[
        "A.",
        "1",
        "1.123"
    ])
    @pytest.mark.xfail
    def test_parse_bad_section_index(self, bad_section_index):
        with pytest.raises(ParseException):
            assert section_index.parseString(bad_section_index,parse_all=True)

    def test_parse_section(self):
        assert section.parseString("1. This is a section.\n",parse_all=True)

    def test_parse_section_with_subs(self):
        assert section.parseString("""1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""", parse_all=True)

    def test_parse_section_with_heading(self):
        assert section.parseString("""
Heading for Section
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    (2) and another subsection.
""", parse_all=True)

    def test_parse_section_with_header_on_sub(self):
        assert section.parseString("""Heading for Section
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs
        (b) and another paragraph,
    Heading for Sub-Section
    (2) and another subsection.
""",parse_all=True)

    def test_parse_empty_section(self):
        # Occasionally, the root section is empty, and only sub-sections
        # have any contents.
        assert section.parseString("1.\n  (1) This is text of the subsection.\n",parse_all=True)

    def test_parse_multiline_section(self):
        parse = section.parseString("1. This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['section text'] == "This is the start and this is the rest"


class TestHeading:
    def test_parse_heading(self):
        assert heading.parseString("\nThis is a heading.\n",parse_all=True)



# test_target = section
class TestTitle:
    def test_parse_title(self):
        assert title.parseString("Rock Paper Scissors Act\n\n",parse_all=True)

class TestAct:
    def test_parse_act(self):
        assert act.parseString("""Rock Paper Scissors Act

Heading
1. This is the text of the RPS Act,
  (1) sub-section text.
""",parse_all=True)

    def test_parse_act_complex(self):
        assert act.parseString("""Rock Paper Scissors Art

Heading
1. This is the start of the section text.
    (1) The section also has sub-sections
        (a) with paragraphs.
            (i) Which have sub-paragraphs

No Main Section
2.
  (1) This is a section with no text and an immediate sub-section.

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
""",parse_all=True)



