from typer.testing import CliRunner
from cards.cli import app
import cards
import pytest
from pathlib import Path
from unittest import mock

import shlex

runner = CliRunner()


def cards_cli(command_string):
    command_list = shlex.split(command_string)
    result = runner.invoke(app, command_list)
    output = result.stdout.rstrip()
    return output


@pytest.fixture()
def mock_cardsdb():
    with mock.patch.object(cards, "CardsDB", autospec=True) as CardsDB:
        yield CardsDB.return_value


def test_version():
    with mock.patch.object(cards, "__version__", "1.2.3"):
        assert cards_cli("version") == "1.2.3"


def test_config(mock_cardsdb):
    mock_cardsdb.path.return_value = "/foo/bar"
    assert cards_cli("config") == "/foo/bar"


def test_count(mock_cardsdb):
    mock_cardsdb.count.return_value = 5
    assert cards_cli("count") == "5"


def test_start(mock_cardsdb):
    cards_cli("start 23")
    mock_cardsdb.start.assert_called_with(23)


def test_finish(mock_cardsdb):
    cards_cli("finish 101")
    mock_cardsdb.finish.assert_called_with(101)


def test_add(mock_cardsdb):
    cards_cli("add some task")
    expected = cards.Card("some task", state="todo")
    mock_cardsdb.add_card.assert_called_with(expected)


def test_add_with_owner(mock_cardsdb):
    cards_cli("add some task -o brian")
    expected = cards.Card("some task", owner="brian", state="todo")
    mock_cardsdb.add_card.assert_called_with(expected)


def test_delete(mock_cardsdb):
    cards_cli("delete 12")
    mock_cardsdb.delete_card.assert_called_with(12)


def test_update(mock_cardsdb):
    cards_cli("update 23 -o okken -s something")
    card = cards.Card("something", owner="okken", state=None)
    mock_cardsdb.update_card.assert_called_with(23, card)


expected_output = """\
                                  
  ID   state   owner   summary    
 ──────────────────────────────── 
  1    todo            some task  
  2    todo            another
                                  
"""


def test_list(mock_cardsdb):
    some_cards = [
        cards.Card("some task", id=1),
        cards.Card("another", id=2),
    ]
    mock_cardsdb.list_cards.return_value = some_cards
    output = cards_cli("list")
    assert output.strip() == expected_output.strip()


def test_main(mock_cardsdb):
    cards_cli("")
    mock_cardsdb.list_cards.assert_called_once()


def test_env_var_path(monkeypatch):
    monkeypatch.setenv("CARDS_DB_DIR", "/foo/bar")
    assert cards.cli.get_path() == Path("/foo/bar")


# Error Cases

def test_delete_invalid(mock_cardsdb):
    mock_cardsdb.delete_card.side_effect = cards.api.InvalidCardId
    out = cards_cli("delete 25")
    assert "Error: Invalid card id 25" in out


def test_start_invalid(mock_cardsdb):
    mock_cardsdb.start.side_effect = cards.api.InvalidCardId
    out = cards_cli("start 25")
    assert "Error: Invalid card id 25" in out


def test_finish_invalid(mock_cardsdb):
    mock_cardsdb.finish.side_effect = cards.api.InvalidCardId
    out = cards_cli("finish 25")
    assert "Error: Invalid card id 25" in out


def test_update_invalid(mock_cardsdb):
    mock_cardsdb.update_card.side_effect = cards.api.InvalidCardId
    out = cards_cli("update 25 -s foo -o okken")
    assert "Error: Invalid card id 25" in out


def test_add_missing_summary(mock_cardsdb):
    mock_cardsdb.add_card.side_effect = cards.api.MissingSummary
    out = cards_cli("add")
    assert "Error: Missing argument 'SUMMARY...'" in out
