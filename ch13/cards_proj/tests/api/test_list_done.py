import pytest


@pytest.mark.num_cards(10)
def test_list_done(cards_db):
    cards_db.finish(3)
    cards_db.finish(5)

    the_list = cards_db.list_done_cards()

    assert len(the_list) == 2
    for card in the_list:
        assert card.id in (3, 5)
        assert card.state == "done"
