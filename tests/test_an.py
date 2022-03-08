from ..clean import *

def test_readme_demo():
    file = open('tests/rps.clean')
    text = file.read()
    file.close()
    parse_result = act.parseString(text,parse_all=True)
    an = generate_act(parse_result)
    assert an == """<?xml version="1.0" encoding="UTF-8"?><akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"><act><preface><p class="title"><shortTitle>Rock Paper Scissors Act Players</shortTitle></p></preface><body><section eId="sec_1"><num>1</num><content><p>A game of rock paper scissors has two players.</p></content></section><section eId="sec_2"><num>2</num><intro><p>There are three signs:</p></intro><subSection eId="sec_2__subsec_1"><num>1</num><content><p>Rock,</p></content></subSection><subSection eId="sec_2__subsec_2"><num>2</num><content><p>Paper, and</p></content></subSection><subSection eId="sec_2__subsec_3"><num>3</num><content><p>Scissors. Defeating Relationships</p></content></subSection></section><section eId="sec_3"><num>3</num><intro><p>The signs have the following relationships:</p></intro><subSection eId="sec_3__subsec_1"><num>1</num><content><p>Rock beats Scissors,</p></content></subSection><subSection eId="sec_3__subsec_2"><num>2</num><content><p>Scissors beats Paper, and</p></content></subSection><subSection eId="sec_3__subsec_3"><num>3</num><content><p>Paper beats Rock. Winner</p></content></subSection></section><section eId="sec_4"><num>4</num><content><p>The winner of a game is the player who throws a sign that beats the sign of the other player.</p></content></section></body></act></akomaNtoso>"""