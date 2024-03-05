import cards

expected = """\

  ID   state   owner   summary    
 ──────────────────────────────── 
  1    done            some task  
  3    done            a third"""


def test_done(cards_db, cards_cli):
    cards_db.add_card(cards.Card("some task", state="done"))
    cards_db.add_card(cards.Card("another"))
    cards_db.add_card(cards.Card("a third", state="done"))
    output = cards_cli("done")
    assert output == expected
