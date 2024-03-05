import pytest
from cards import Card, InvalidCardId
import time


@pytest.mark.smoke
def test_start(cards_db):
    """
    start changes state from "todo" to "in prog"
    """
    i = cards_db.add_card(Card("foo", state="todo"))
    cards_db.start(i)
    c = cards_db.get_card(i)
    time.sleep(5)
    assert c.state == "in prog"


@pytest.mark.smok
@pytest.mark.exception
def test_start_non_existent(cards_db):
    """
    Shouldn't be able to start a non-existent card.
    """
    any_number = 123  # any number will be invalid, db is empty
    with pytest.raises(InvalidCardId):
        cards_db.start(any_number)
