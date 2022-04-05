import pytest
from ..clean import *

class TestIndents:

# Note that parseString returns ParseResults([],{}) if all of the
# elements of the parse are suppressed, and that ParseResults([],{})
# is falsish. Therefore, to test for parsing of items that are
# completely suppressed, you assert that .dump() returns anything.

    def test_indent(self):
        assert UP.parseString("\nINDENT",parse_all=True).dump()

    def test_undent(self):
        assert DOWN.parseString("\nUNDENT",parse_all=True).dump()

    def test_blank(self):
        assert BLANK_LINE.parseString("\n",parse_all=True).dump()

    @pytest.mark.parametrize('numpart',[
        "\n(i)",
        "\n(a)",
        "\n1.",
        "\n(1)",
        "\nUNDENT"
    ])
    def test_numpart(self,numpart):
        assert numbered_part.parseString(numpart,parse_all=True).dump()

    def test_indented_subparas(self):
        parse = (UP + sub_paragraph_list + DOWN).parseString("""
INDENT
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

class TestLegalText:

    def test_multiline_works(self):
        assert legal_text.parseString("text starting\nand continuing.",parse_all=True)

    @pytest.mark.parametrize("numpart",[
        "1.",
        "(1)",
        "\n",
        "(a)",
        "(i)",
        "INDENT",
        "UNDENT"
    ])
    def test_stops_on_new_numpart(self,numpart):
        text = "This is the start\nand this is the rest\n" + numpart
        parse = legal_text.parseString(text)
        assert parse.as_list()[0] == "This is the start and this is the rest"

    def test_nothing_is_legal_text(self):
        assert legal_text.parseString("",parse_all=True).dump()

    def test_legal_text_can_be_one_word(self):
        assert legal_text.parseString("test",parse_all=True)
    
    def test_legal_text_can_be_multiple_words(self):
        assert legal_text.parseString("test this",parse_all=True)
    
    def test_legal_text_can_include_spans(self):
        text = "This is the [span]{legal text} here"
        parse = legal_text.parseString(text,parse_all=True)
        assert parse.as_list()[1] == [['span'],['legal text']]
    
    def test_multi_line_spans(self):
        text = "This is a [span]{divided\nover} two lines"
        parse = legal_text.parseString(text,parse_all=True)
        assert parse.as_list()[1] == [['span'],['divided over']]

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
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest",parse_all=True)
        assert parse.asDict()['sub-paragraph text'] == ["This is the start and this is the rest"]

    def test_parse_multiline_subpara_stop_new(self):
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest\n(ii) Test ignore")
        assert parse.asDict()['sub-paragraph text'] == ["This is the start and this is the rest"]

    def test_parse_multiline_subpara_stop_para(self):
        parse = sub_paragraph.parseString("\n(i) This is the start\nand this is the rest\nUNDENT\n(b) test ignore")
        assert parse.asDict()['sub-paragraph text'] == ["This is the start and this is the rest"]

    def test_subpara_structure(self):
        parse = sub_paragraph.parseString("\n(i) Sub-paragraph here",parse_all=True)
        dictionary = parse.asDict()
        assert dictionary == \
            {
                'sub-paragraph index': ["i"],
                'sub-paragraph text': ["Sub-paragraph here"]
            }

    def test_parse_subparalist(self):
        parse = sub_paragraph_list.parseString("""
(i) subparagraph one
(ii) subparagraph two""",parse_all=True)
        assert parse

    
    def test_subparalist_structure(self):
        parse = sub_paragraph_list.parseString("""
(i) subparagraph one
(ii) subparagraph two""",parse_all=True)
        assert len(parse) == 2
        assert parse[0].asDict() == \
                {
                    'sub-paragraph index': ["i"],
                    'sub-paragraph text': ["subparagraph one"]
                }
        assert parse[1].asDict() == \
                {
                    'sub-paragraph index': ["ii"],
                    'sub-paragraph text': ["subparagraph two"]
                }
    
    def test_subpara_index_insert_structure(self):
        text = "\n(i.1) Test"
        parse = sub_paragraph.parseString(text,parse_all=True)
        dictionary = parse.asDict()
        assert dictionary == {
            'sub-paragraph index': ['i.1'],
            'sub-paragraph text': ["Test"]
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
        assert paragraph.parseString("\n(a) This is paragraph.",parse_all=True)

    def test_parse_paragraph_with_subs(self):
        assert paragraph.parseString("""
(a) this is a paragraph
INDENT
(i) with a subparagraph, and
(ii) another subparagraph.
UNDENT""",parse_all=True)

    def test_parse_sandwich_paragraph(self):
        parse = paragraph.parseString("\n(a) This is the intro\nINDENT\n(i) this is the sub-para, and\nUNDENT\nthere is concluding sandwich text.",parse_all=True)
        assert parse.asDict()['sub-paragraphs'][0]['sub-paragraph text'] == ["this is the sub-para, and"]
        assert parse.asDict()['paragraph post'] == ["there is concluding sandwich text."]

    def test_parse_multiline_paragraph(self):
        parse = paragraph.parseString("\n(a) This is the start\nand this is the rest",parse_all=True)
        assert parse.asDict()['paragraph text'] == ["This is the start and this is the rest"]


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
        "\n(x)"
    ])
    @pytest.mark.xfail
    def test_parse_bad_sub_section_index(self, bad_sub_section_index):
        with pytest.raises(ParseException):
            assert sub_section_index.parseString(bad_sub_section_index,parse_all=True)

    def test_parse_subsection(self):
        assert sub_section.parseString("\n(1) This is a subsection.",parse_all=True)

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
        parse = sub_section.parseString("\n(1) This is the start\nand this is the rest",parse_all=True)
        assert parse.asDict()['sub-section text'] == ["This is the start and this is the rest"]


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

    def test_parse_section_with_header_on_sub2(self):
        assert sub_section_list.parseString("""
(1) The section also has sub-sections
INDENT
(a) with paragraphs.
INDENT
(i) Which have sub-paragraphs
UNDENT
(b) and another paragraph,
UNDENT

Heading for Sub-Section
(2) and another subsection.""",parse_all=True)

    def test_parse_empty_titled_section(self):
        assert empty_section.parseString("\n\nHeading\n1.\nINDENT\n(1) Subsection\nUNDENT",parse_all=True)

    def test_parse_empty_section(self):
        # Occasionally, the root section is empty, and only sub-sections
        # have any contents.
        assert section.parseString("\n1.\nINDENT\n(1) This is text of the subsection.\nUNDENT",parse_all=True)

    def test_parse_multiline_section(self):
        parse = section.parseString("\n1. This is the start\nand this is the rest",parse_all=True)
        assert parse.asDict()['section text'] == ["This is the start and this is the rest"]

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
        assert dictionary['section post'] == []

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
        assert dictionary['section post'] == ["target sandwich"]

class TestHeading:
    def test_parse_heading(self):
        assert heading.parseString("\n\nThis is a heading.",parse_all=True)



class TestTitle:
    def test_parse_title(self):
        parse = title.parseString("Rock Paper Scissors Act",parse_all=False) 
        assert parse.as_list() == ['Rock Paper Scissors Act']

class TestAct:
    def test_parse_act(self):
        assert act.parseString("""Rock Paper Scissors Act

Heading
1. This is the text of the RPS Act,
INDENT
(1) sub-section text.
UNDENT""",parse_all=True)

    def test_one_index(self):
        text = """Act

1.1. First section."""
        parse = act.parse_string(text,parse_all=True)
        assert len(parse['body']) == 1

    def test_parse_act_complex(self):
        assert act.parseString("""Rock Paper Scissors Act

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
        string = "[text]"
        parse = span_name.parseString(string,parse_all=True)
        dictionary = parse.asList()
        assert dictionary == ['text']

    def test_span(self):
        parse = span.parseString("[text]{this is some legal text}",parse_all=True)
        dictionary = parse.asDict()
        assert dictionary['span name'] == ["text"] and dictionary['span body'] == ['this is some legal text']
    
    def test_span_can_have_internal_quotations(self):
        parse = span.parseString("[name]{this is text's possessive}",parse_all=True)
        assert parse

    def test_nested_spans(self):
        parse = span.parseString("[text]{outer span has [inner]{another span} in it}", parse_all=True)
        output = parse.asList()
        assert output == [['text'], ['outer span has', [['inner'], ['another span']], 'in it']]

    def test_nested_spans_in_para(self):
        parse = legal_text.parseString("""This is a test
of a paragraph with [span1]{ nested
spans [inner]{inside} it} including
across lines.""",parse_all=True)
        assert parse.as_list() == [
            'This is a test of a paragraph with',
            [
                ['span1'],
                [
                    'nested spans', 
                    [
                        ['inner'], 
                        ['inside']
                    ],
                     'it'
                ]
            ],
            'including across lines.'
        ]

    def test_spans_on_new_line(self):
        parse = legal_text.parseString("""This is a test
[of] {a paragraph with} including
across lines.""",parse_all=True)
        assert parse.as_list() == [
            'This is a test',
            [
                ['of'],
                ['a paragraph with']
            ],
            'including across lines.'
        ]


class TestR34:
    def test_long_example(self):
        with open('clean/tests/r34.clean','r') as file:
            parse = act.parseString(addExplicitIndents(file.read()),parse_all=True)
            assert parse

    def test_long_example_with_spans(self):
        with open('clean/tests/r34span.clean','r') as file:
            parse = act.parseString(addExplicitIndents(file.read()),parse_all=True)
            assert parse

    def test_long_example_with_spans_structure(self):
        with open('clean/tests/r34span.clean','r') as file:
            parse = act.parseString(addExplicitIndents(file.read()),parse_all=True)
            assert parse['body'][0]['sub-sections'][0]['paragraphs'][3].as_list() == ['d', 'any business which involves', [['fees'], ["the sharing of the legal practitioner's fees with"]], ', or', [['commission'], ['the payment of a commission to']], ', any unauthorised person for legal work performed by the legal practitioner;']