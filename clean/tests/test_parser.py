import pytest
from ..clean import *

class TestIndents:

# Note that parseString returns ParseResults([],{}) if all of the
# elements of the parse are suppressed, and that ParseResults([],{})
# is falsish. Therefore, to test for parsing of items that are
# completely suppressed, you assert that .dump() returns anything.

    def test_indent(self):
        assert UP.parseString("INDENT",parse_all=True).dump()

    def test_undent(self):
        assert DOWN.parseString("UNDENT",parse_all=True).dump()

    def test_blank(self):
        assert BLANK_LINE.parseString("\n",parse_all=True).dump()

    @pytest.mark.parametrize('numpart',[
        "\n   (i)",
        "\n (a)",
        "\n1.",
        "\n(1)",
        "UNDENT"
    ])
    def test_numpart(self,numpart):
        assert numbered_part.parseString(numpart,parse_all=True).dump()

    def test_indented_subparas(self):
        parse = (UP + sub_paragraph_list + DOWN).parseString("""INDENT
    (i) with a subparagraph, and
    (ii) another subparagraph.
UNDENT""", parse_all=True)
        assert parse

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
        "\n(viii)",
        "\n(c)",
        "\n(i.123.4)",
        "\n(iv.5)"
    ])
    def test_parse_subpara_index(self, good_subparagraph_index):
        assert sub_paragraph_index.parseString(good_subparagraph_index,parse_all=True)

    @pytest.mark.parametrize("bad_subparagraph_index",[
        "\n(b)", #Must be roman numerals
        "\n(M)", # must be lower-case
        "\n(iivivi)", # must be well-formed roman numeral
    ])
    def test_parse_bad_subpara_index(self, bad_subparagraph_index):
        with pytest.raises(ParseException):
            assert sub_paragraph_index.parseString(bad_subparagraph_index,parse_all=True)

    def test_parse_subpara(self):
        parse = sub_paragraph.parseString("\n(i) Sub-paragraph here",parse_all=True) 
        assert parse

    def test_parse_multiline_subpara(self):
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_parse_multiline_subpara_stop_new(self):
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest\n(ii) Test ignore")
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_parse_multiline_subpara_stop_para(self):
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest\nUNDENT\n(b) test ignore")
        assert parse.asDict()['sub-paragraph text'] == "This is the start and this is the rest"

    def test_subpara_structure(self):
        parse = sub_paragraph.parseString("\n(i) Sub-paragraph here",parse_all=True)
        dictionary = parse.asDict()
        assert dictionary == \
            {
                'sub-paragraph index': ["i"],
                'sub-paragraph text': "Sub-paragraph here"
            }

    def test_parse_subparalist(self):
        parse = sub_paragraph_list.parseString("""\n(i) subparagraph one
    (ii) subparagraph two""",parse_all=True)
        assert parse

    
    def test_subparalist_structure(self):
        parse = sub_paragraph_list.parseString("""\n(i) subparagraph one
    (ii) subparagraph two""",parse_all=True)
        assert len(parse) == 2
        assert parse[0].asDict() == \
                {
                    'sub-paragraph index': ["i"],
                    'sub-paragraph text': "subparagraph one"
                }
        assert parse[1].asDict() == \
                {
                    'sub-paragraph index': ["ii"],
                    'sub-paragraph text': "subparagraph two"
                }
    
    def test_subpara_index_insert_structure(self):
        text = "\n(i.1) Test"
        parse = sub_paragraph.parseString(text,parse_all=True)
        dictionary = parse.asDict()
        assert dictionary == {
            'sub-paragraph index': ['i.1'],
            'sub-paragraph text': "Test"
        }

class TestParagraph:
    @pytest.mark.parametrize("good_paragraph_index",[
        "\n(aa)",
        "\n(ab.1)",
        "\n(aaa.1.2345)"
    ])
    def test_parse_paragraph_index(self, good_paragraph_index):
        assert paragraph_index.parseString(good_paragraph_index,parse_all=True)

    @pytest.mark.parametrize("bad_paragraph_index",[
        "\n(1a)",
        "\n<a>",
        "\n(a1)",
        "\n(aa",
        "\na)",
        "\n(A)",
        "(a)"
    ])
    @pytest.mark.xfail
    def test_parse_bad_paragraph_index(self, bad_paragraph_index):
        with pytest.raises(ParseException):
            assert paragraph_index.parseString(bad_paragraph_index,parse_all=True)

    def test_parse_paragraph_index_structure(self):
        assert paragraph_index.parseString("\n(a)",parse_all=True).asList() == ['a']

    def test_parse_paragraph(self):
        assert paragraph.parseString("\n(a) This is paragraph.\n",parse_all=True)

    def test_parse_paragraph_with_subs(self):
        assert paragraph.parseString("""
(a) this is a paragraph
INDENT
    (i) with a subparagraph, and
    (ii) another subparagraph.
UNDENT""",parse_all=True)

    def test_parse_sandwich_paragraph(self):
        parse = paragraph.parseString("\n(a) This is the intro\nINDENT\n  (i) this is the sub-para, and\nUNDENT\nthere is concluding sandwich text.",parse_all=True)
        assert parse.asDict()['sub-paragraphs'][0]['sub-paragraph text'] == "this is the sub-para, and"
        assert parse.asDict()['paragraph post'] == "there is concluding sandwich text."

    def test_parse_multiline_paragraph(self):
        parse = paragraph.parseString("\n(a) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['paragraph text'] == "This is the start and this is the rest"


class TestSubSection:
    @pytest.mark.parametrize("good_sub_section_index",[
        "\n(12)",
        "\n(4.1)",
        "\n(234.1.2345)"
    ])
    def test_parse_sub_section_index(self, good_sub_section_index):
        assert sub_section_index.parseString(good_sub_section_index,parse_all=True)

    @pytest.mark.parametrize("bad_sub_section_index",[
        "\n(12a)",
        "\n(4.1",
        "\n234.1.2345)",
        "\n(x)",
        "(1)"
    ])
    @pytest.mark.xfail
    def test_parse_bad_sub_section_index(self, bad_sub_section_index):
        with pytest.raises(ParseException):
            assert sub_section_index.parseString(bad_sub_section_index,parse_all=True)

    def test_parse_subsection(self):
        assert sub_section.parseString("\n(1) This is a subsection.\n",parse_all=True)

    def test_parse_subsection_with_paras(self):
        assert sub_section.parseString("""
(1) this is a subsection, with
INDENT
    (a) this as a paragraph, and
INDENT
        (i) with a subparagraph, and
        (ii) another subparagraph, followed by
UNDENT
    (b) another paragraph.
UNDENT""", parse_all=True)

    def test_parse_sandwich_subsection_with_paras(self):
        assert sub_section.parseString("""
(1) this is a subsection, with
INDENT
    (a) this as a paragraph, and
INDENT
        (i) with a subparagraph, and
        (ii) another subparagraph, followed by
UNDENT
    (b) another paragraph.
UNDENT
and this closing text.""", parse_all=True)


    def test_parse_multiline_subsection(self):
        parse = sub_section.parseString("\n(1) This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['sub-section text'] == "This is the start and this is the rest"


class TestSection:
    
    @pytest.mark.parametrize("good_section_index",[
        "\n1.",
        "\n12345.",
        "\n1.2."
    ])
    def test_parse_section_index(self, good_section_index):
        assert section_index.parseString(good_section_index,parse_all=True)

    @pytest.mark.parametrize("bad_section_index",[
        "\nA.",
        "\n1",
        "\n1.123",
        "1."
    ])
    @pytest.mark.xfail
    def test_parse_bad_section_index(self, bad_section_index):
        with pytest.raises(ParseException):
            assert section_index.parseString(bad_section_index,parse_all=True)

    def test_parse_section(self):
        assert section.parseString("\n1. This is a section.",parse_all=True)

    def test_parse_section_with_subs(self):
        assert section.parseString("""
1. This is the start of the section text.
INDENT
    (1) The section also has sub-sections
INDENT
        (a) with paragraphs.
INDENT
            (i) Which have sub-paragraphs
UNDENT
        (b) and another paragraph,
UNDENT
    (2) and another subsection.
UNDENT""", parse_all=True)

    def test_parse_section_with_heading(self):
        assert section.parseString("""
Heading for Section
1. This is the start of the section text.
INDENT
    (1) The section also has sub-sections
INDENT
        (a) with paragraphs.
INDENT
            (i) Which have sub-paragraphs
UNDENT
        (b) and another paragraph,
UNDENT
    (2) and another subsection.
UNDENT""", parse_all=True)

    def test_parse_section_with_header_on_sub(self):
        assert section.parseString("""
Heading for Section
1. This is the start of the section text.
INDENT
    (1) The section also has sub-sections
INDENT
        (a) with paragraphs.
INDENT
            (i) Which have sub-paragraphs
UNDENT
        (b) and another paragraph,
UNDENT

    Heading for Sub-Section
    (2) and another subsection.
UNDENT""",parse_all=True)

    def test_parse_empty_section(self):
        # Occasionally, the root section is empty, and only sub-sections
        # have any contents.
        assert section.parseString("\n1.\nINDENT\n  (1) This is text of the subsection.\nUNDENT",parse_all=True)

    def test_parse_multiline_section(self):
        parse = section.parseString("\n1. This is the start\nand this is the rest\n",parse_all=True)
        assert parse.asDict()['section text'] == "This is the start and this is the rest"

    def test_parse_section_to_paragraph(self):
        text = """
3. This is a section
INDENT
    (a) with direct paragraphs,
    (b) like this,
UNDENT"""
        parse = section.parseString(text,parse_all=True)
        assert parse

    def test_blank_lines_prevent_sandwich(self):
        text = """
1. This is start
INDENT
  (1) this is sub
UNDENT

this is not sandwich"""
        parse = section.parseString(text)
        dictionary = parse.asDict()
        assert dictionary['section post'] ==''

    def test_blank_links_interrupt_sandwich(self):
        text = """
1. This is start
INDENT
  (1) this is sub
UNDENT
target sandwich

this is not sandwich"""
        parse = section.parseString(text)
        dictionary = parse.asDict()
        assert dictionary['section post'] == "target sandwich"

class TestHeading:
    def test_parse_heading(self):
        assert heading.parseString("\nThis is a heading.",parse_all=True)



class TestTitle:
    def test_parse_title(self):
        assert title.parseString("Rock Paper Scissors Act\n",parse_all=True)

class TestAct:
    def test_parse_act(self):
        assert act.parseString("""Rock Paper Scissors Act

Heading
1. This is the text of the RPS Act,
INDENT
  (1) sub-section text.
UNDENT""",parse_all=True)

    def test_parse_act_complex(self):
        assert act.parseString("""Rock Paper Scissors Art

Heading
1. This is the start of the section text.
INDENT
    (1) The section also has sub-sections
INDENT
        (a) with paragraphs.
INDENT
            (i) Which have sub-paragraphs
UNDENT
UNDENT
UNDENT

No Main Section
2.
INDENT
  (1) This is a section with no text and an immediate sub-section.
UNDENT

Sandwiches
3. This is a section
INDENT
    (a) with direct paragraphs,
    (b) like this,
UNDENT
and sandwich text.

Multi-line Text
4. This is a section where the text continues
across more than one line, and should
all be treated as the same piece of text,
INDENT
    (1) followed by a subsection, which also
    extends across more than one line.
UNDENT""",parse_all=True)

class TestSpan:
    def test_span_name(self):
        assert span_name.parseString("[text]",parse_all=True)

    def test_span(self):
        assert span.parseString("[text]{this is some legal text}",parse_all=True)
    
    def test_nested_spans(self):
        assert False

    def nested_spans_in_para(self):
        assert False

