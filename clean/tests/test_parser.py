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

    def test_parse_empty_titled_section(self):
        assert empty_section.parseString("\nHeading\n1.\nINDENT\n  (1) Subsection\nUNDENT",parse_all=True)

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
        string = "[text]"
        parse = span_name.parseString(string,parse_all=True)
        dictionary = parse.asDict()
        assert dictionary['span name'] == 'text'

    def test_span(self):
        parse = span.parseString("[text]{this is some legal text}",parse_all=True)
        dictionary = parse.asDict()
        assert dictionary['span name'] == "text" and dictionary['span'] == "this is some legal text"
    
    def test_nested_spans(self):
        parse = span.parseString("[text]{outer span has [inner]{another span} in it}", parse_all=True)
        output = parse.asList() 
        #TODO I'm not even sure what this should be producing, yet.
        assert False

    def test_nested_spans_in_para(self):
        assert legal_text.parseString("""1. This is a test
of a paragraph with [span1]{ nested
spans [inner]{inside} it} including
across lines.""",parse_all=True)

    def test_nested_spans_in_para_structure(self):
        string = """1. This is a test
of a paragraph with [span1]{ nested
spans [inner]{inside} it} including
across lines."""
        parse = legal_text.parseString(string,parse_all=True)
        dictionary = parse.asDict()
        assert False

class TestR34:
    def test_long_example(self):
        with open('clean/tests/r34.clean','r') as file:
            parse = act.parseString(file.read(),parse_all=False)
            assert parse
    
    def test_section(self):
        text = addExplicitIndents("""
Executive appointments
34.
  (1) A legal practitioner must not accept any executive appointment associated with any of the following businesses:
    (a) any business which detracts from, is incompatible with, or derogates from the dignity of, the legal profession;
    (b) any business which materially interferes with -
      (i) the legal practitioner’s primary occupation of practising as a lawyer;
      (ii) the legal practitioner’s availability to those who may seek the legal practitioner’s services as a lawyer; or
      (iii) the representation of the legal practitioner’s clients;
    (c) any business which is likely to unfairly attract business in the practice of law;
    (d) any business which involves the sharing of the legal practitioner’s fees with, or the payment of a commission to, any unauthorised person for legal work performed by the legal practitioner;
    (e) any business set out in the First Schedule;
    (f) any business which is prohibited by -
      (i) the Act;
      (ii) these Rules or any other subsidiary legislation made under the Act;
      (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act; or
      (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
  (2) Subject to paragraph (1), a legal practitioner in a Singapore law practice (called in this paragraph the main practice) may accept an executive appointment in another Singapore law practice (called in this paragraph the related practice), if the related practice is connected to the main practice in either of the following ways:
    (a) every legal or beneficial owner of the related practice is the sole proprietor, or a partner or director, of the main practice;
    (b) the legal practitioner accepts the executive appointment as a representative of the main practice in the related practice, and the involvement of the main practice in the related practice is not prohibited by any of the following:
      (i) the Act;
      (ii) these Rules or any other subsidiary legislation made under the Act;
      (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act;
      (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
  (3) Subject to paragraph (1), a legal practitioner may accept an executive appointment in a business entity which provides law-related services.
  (4) Subject to paragraph (1), a legal practitioner (not being a locum solicitor) may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
  (5) Despite paragraph (1)(b), but subject to paragraph (1)(a) and (c) to (f), a locum solicitor may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
  (6) Except as provided in paragraphs (2) to (5) -
    (a) a legal practitioner in a Singapore law practice must not accept any executive appointment in another Singapore law practice; and
    (b) a legal practitioner must not accept any executive appointment in a business entity.
  (7) To avoid doubt, nothing in this rule prohibits a legal practitioner from accepting any appointment in any institution set out in the Third Schedule.
  (8) To avoid doubt, this rule does not authorise the formation of, or regulate -
    (a) any related practice referred to in paragraph (2); or
    (b) any business entity referred to in paragraph (3), (4) or (5).
  (9) In this rule and the First to Fourth Schedules -
    (a) "business" includes any business, trade or calling in Singapore or elsewhere, whether or not for the purpose of profit, but excludes the practice of law;
    (b) "business entity)  -
      (i) includes any company, corporation, partnership, limited liability partnership, sole proprietorship, business trust or other entity that carries on any business; but
      (ii) excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, any foreign law practice and any institution set out in the Third Schedule;
    (c) "executive appointment" means a position associated with a business, or in a business entity or Singapore law practice, which entitles the holder of the position to perform executive functions in relation to the business, business entity or Singapore law practice (as the case may be), but excludes any non‑executive director or independent director associated with the business or in the business entity;
    (d) "law-related service" means any service set out in the Fourth Schedule, being a service that may reasonably be performed in conjunction with, and that is in substance related to, the provision of any legal service.""")
        assert section.parseString(text,parse_all=True)

    def test_empty_section(self):
        text = addExplicitIndents("""
Executive appointments
34.
  (1) A legal practitioner must not accept any executive appointment associated with any of the following businesses:
    (a) any business which detracts from, is incompatible with, or derogates from the dignity of, the legal profession;
    (b) any business which materially interferes with -
      (i) the legal practitioner’s primary occupation of practising as a lawyer;
      (ii) the legal practitioner’s availability to those who may seek the legal practitioner’s services as a lawyer; or
      (iii) the representation of the legal practitioner’s clients;
    (c) any business which is likely to unfairly attract business in the practice of law;
    (d) any business which involves the sharing of the legal practitioner’s fees with, or the payment of a commission to, any unauthorised person for legal work performed by the legal practitioner;
    (e) any business set out in the First Schedule;
    (f) any business which is prohibited by -
      (i) the Act;
      (ii) these Rules or any other subsidiary legislation made under the Act;
      (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act; or
      (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
  (2) Subject to paragraph (1), a legal practitioner in a Singapore law practice (called in this paragraph the main practice) may accept an executive appointment in another Singapore law practice (called in this paragraph the related practice), if the related practice is connected to the main practice in either of the following ways:
    (a) every legal or beneficial owner of the related practice is the sole proprietor, or a partner or director, of the main practice;
    (b) the legal practitioner accepts the executive appointment as a representative of the main practice in the related practice, and the involvement of the main practice in the related practice is not prohibited by any of the following:
      (i) the Act;
      (ii) these Rules or any other subsidiary legislation made under the Act;
      (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act;
      (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
  (3) Subject to paragraph (1), a legal practitioner may accept an executive appointment in a business entity which provides law-related services.
  (4) Subject to paragraph (1), a legal practitioner (not being a locum solicitor) may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
  (5) Despite paragraph (1)(b), but subject to paragraph (1)(a) and (c) to (f), a locum solicitor may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
  (6) Except as provided in paragraphs (2) to (5) -
    (a) a legal practitioner in a Singapore law practice must not accept any executive appointment in another Singapore law practice; and
    (b) a legal practitioner must not accept any executive appointment in a business entity.
  (7) To avoid doubt, nothing in this rule prohibits a legal practitioner from accepting any appointment in any institution set out in the Third Schedule.
  (8) To avoid doubt, this rule does not authorise the formation of, or regulate -
    (a) any related practice referred to in paragraph (2); or
    (b) any business entity referred to in paragraph (3), (4) or (5).
  (9) In this rule and the First to Fourth Schedules -
    (a) "business" includes any business, trade or calling in Singapore or elsewhere, whether or not for the purpose of profit, but excludes the practice of law;
    (b) "business entity"  -
      (i) includes any company, corporation, partnership, limited liability partnership, sole proprietorship, business trust or other entity that carries on any business; but
      (ii) excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, any foreign law practice and any institution set out in the Third Schedule;
    (c) "executive appointment" means a position associated with a business, or in a business entity or Singapore law practice, which entitles the holder of the position to perform executive functions in relation to the business, business entity or Singapore law practice (as the case may be), but excludes any non‑executive director or independent director associated with the business or in the business entity;
    (d) "law-related service" means any service set out in the Fourth Schedule, being a service that may reasonably be performed in conjunction with, and that is in substance related to, the provision of any legal service.""")
        assert empty_section.parseString(text,parse_all=True)

    def test_sub_section_list(self):
        text = addExplicitIndents("""
(1) A legal practitioner must not accept any executive appointment associated with any of the following businesses:
  (a) any business which detracts from, is incompatible with, or derogates from the dignity of, the legal profession;
  (b) any business which materially interferes with -
    (i) the legal practitioner’s primary occupation of practising as a lawyer;
    (ii) the legal practitioner’s availability to those who may seek the legal practitioner’s services as a lawyer; or
    (iii) the representation of the legal practitioner’s clients;
  (c) any business which is likely to unfairly attract business in the practice of law;
  (d) any business which involves the sharing of the legal practitioner’s fees with, or the payment of a commission to, any unauthorised person for legal work performed by the legal practitioner;
  (e) any business set out in the First Schedule;
  (f) any business which is prohibited by -
    (i) the Act;
    (ii) these Rules or any other subsidiary legislation made under the Act;
    (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act; or
    (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
(2) Subject to paragraph (1), a legal practitioner in a Singapore law practice (called in this paragraph the main practice) may accept an executive appointment in another Singapore law practice (called in this paragraph the related practice), if the related practice is connected to the main practice in either of the following ways:
  (a) every legal or beneficial owner of the related practice is the sole proprietor, or a partner or director, of the main practice;
  (b) the legal practitioner accepts the executive appointment as a representative of the main practice in the related practice, and the involvement of the main practice in the related practice is not prohibited by any of the following:
    (i) the Act;
    (ii) these Rules or any other subsidiary legislation made under the Act;
    (iii) any practice directions, guidance notes and rulings issued under section 71(6) of the Act;
    (iv) any practice directions, guidance notes and rulings (relating to professional practice, etiquette, conduct and discipline) issued by the Council or the Society.
(3) Subject to paragraph (1), a legal practitioner may accept an executive appointment in a business entity which provides law-related services.
(4) Subject to paragraph (1), a legal practitioner (not being a locum solicitor) may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
(5) Despite paragraph (1)(b), but subject to paragraph (1)(a) and (c) to (f), a locum solicitor may accept an executive appointment in a business entity which does not provide any legal services or law-related services, if all of the conditions set out in the Second Schedule are satisfied.
(6) Except as provided in paragraphs (2) to (5) -
  (a) a legal practitioner in a Singapore law practice must not accept any executive appointment in another Singapore law practice; and
  (b) a legal practitioner must not accept any executive appointment in a business entity.
(7) To avoid doubt, nothing in this rule prohibits a legal practitioner from accepting any appointment in any institution set out in the Third Schedule.
(8) To avoid doubt, this rule does not authorise the formation of, or regulate -
  (a) any related practice referred to in paragraph (2); or
  (b) any business entity referred to in paragraph (3), (4) or (5).
(9) In this rule and the First to Fourth Schedules -
  (a) "business" includes any business, trade or calling in Singapore or elsewhere, whether or not for the purpose of profit, but excludes the practice of law;
  (b) "business entity"  -
    (i) includes any company, corporation, partnership, limited liability partnership, sole proprietorship, business trust or other entity that carries on any business; but
    (ii) excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, any foreign law practice and any institution set out in the Third Schedule;
  (c) "executive appointment" means a position associated with a business, or in a business entity or Singapore law practice, which entitles the holder of the position to perform executive functions in relation to the business, business entity or Singapore law practice (as the case may be), but excludes any non‑executive director or independent director associated with the business or in the business entity;
  (d) "law-related service" means any service set out in the Fourth Schedule, being a service that may reasonably be performed in conjunction with, and that is in substance related to, the provision of any legal service.""")
        assert sub_section_list.parseString(text,parse_all=True)

    def test_sub_section(self):
        text = addExplicitIndents("""
(9) In this rule and the First to Fourth Schedules
  (a) "business" includes any business, trade or calling in Singapore or elsewhere, whether or not for the purpose of profit, but excludes the practice of law;
  (b) "business entity"  -
    (i) includes any company, corporation, partnership, limited liability partnership, sole proprietorship, business trust or other entity that carries on any business; but
    (ii) excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, any foreign law practice and any institution set out in the Third Schedule;
  (c) "executive appointment" means a position associated with a business, or in a business entity or Singapore law practice, which entitles the holder of the position to perform executive functions in relation to the business, business entity or Singapore law practice (as the case may be), but excludes any non‑executive director or independent director associated with the business or in the business entity;
  (d) "law-related service" means any service set out in the Fourth Schedule, being a service that may reasonably be performed in conjunction with, and that is in substance related to, the provision of any legal service.
""")
        parse = sub_section.parseString(text,parse_all=False) 
        assert parse

    def test_paragraph_list(self):
        text = addExplicitIndents("""
(a) "business" includes any business, trade or calling in Singapore or elsewhere, whether or not for the purpose of profit, but excludes the practice of law;
(b) "business entity"  
  (i) includes any company, corporation, partnership, limited liability partnership, sole proprietorship, business trust or other entity that carries on any business; but
  (ii) excludes any Singapore law practice, any Joint Law Venture, any Formal Law Alliance, any foreign law practice and any institution set out in the Third Schedule;
(c) "executive appointment" means a position associated with a business, or in a business entity or Singapore law practice, which entitles the holder of the position to perform executive functions in relation to the business, business entity or Singapore law practice (as the case may be), but excludes any non-executive director or independent director associated with the business or in the business entity;
(d) "law-related service" means any service set out in the Fourth Schedule, being a service that may reasonably be performed in conjunction with, and that is in substance related to, the provision of any legal service.""")
        parse = paragraph_list.parseString(text,parse_all=True) 
        assert parse