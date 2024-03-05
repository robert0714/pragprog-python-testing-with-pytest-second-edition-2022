import subprocess


def test_version_v1():
    process = subprocess.run(
        ["cards", "version"], capture_output=True, text=True
    )
    output = process.stdout.rstrip()
    assert output == cards.__version__


import cards


def test_version_v2(capsys):
    cards.cli.version()
    output = capsys.readouterr().out.rstrip()
    assert output == cards.__version__


from typer.testing import CliRunner


def test_version_v3():
    runner = CliRunner()
    result = runner.invoke(cards.app, ["version"])
    output = result.output.rstrip()
    assert output == cards.__version__


def test_db_location(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(cards.app, ["config"])
    db_location = result.output.rstrip()
    print(f"{db_location=}")
