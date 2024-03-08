# Chapter 13 Debugging Test Failures
Test failures happen. If they didn’t, tests wouldn’t be much use. What we do when tests fail is what counts. When tests fail, we need to figure out why. It might be the test or it might be the application. The process of determining where the problem lies and what to do about it is similar.

Integrated development environments (IDEs) and many text editors have graphical debuggers built right in. These tools are incredibly helpful for debugging, allowing us to add breakpoints, step through code, look at variable values, and much more. However, pytest also provides many tools that may help you solve the problem faster, without having to reach for a debugger. There are also times when IDEs may be difficult to use, such as while debugging code on a remote system or when debugging one tox environment. Python includes a builtin source code debugger called ``pdb``, as well as several flags to make debugging with ``pdb`` quick and easy.

In this chapter, we’re going to debug some failing code with the help of pytest flags and ``pdb``. You may spot the bugs right away. Wonderful. We’re just using the bug as an excuse to look at debugging flags and the pytest plus ``pdb`` integration.

We need a failing test to debug. For that, we’ll go back to the Cards project—this time in developer mode—to add a feature and some tests.
## Adding a New Feature to the Cards Project
Let’s say we’ve been using Cards for a while and we now have some finished tasks:
```bash
​ 	​$ ​​cards​​ ​​list​
​ 	
​ 	  ID   state   owner   summary
​ 	 ────────────────────────────────
​ 	  1    done            some task
​ 	  2    todo            another
​ 	  3    done            a third
```

We’d like to list all of the completed tasks at the end of the week. We can do this with cards list already, because it has some filter features:
```bash

​ 	​$ ​​cards​​ ​​list​​ ​​--help​
​ 	Usage: cards list [OPTIONS]
​ 	
​ 	  List cards in db.
​ 	
​ 	Options:
​ 	  -o, --owner TEXT
​ 	  -s, --state TEXT
​ 	  --help            Show this message and exit.
​ 	
​ 	​$ ​​cards​​ ​​list​​ ​​--state​​ ​​done​
​ 	
​ 	  ID   state   owner   summary
​ 	 ────────────────────────────────
​ 	  1    done            some task
​ 	  3    done            a third
```
That works. But let’s add a cards done command to do this filter for us. For that, we need a CLI command:

[ch13/cards_proj/src/cards/cli.py](./cards_proj/src/cards/cli.py?plain=1#L55-L62)
```python
​ 	@app.command(​"done"​)
​ 	​def​ ​list_done_cards​():
​ 	    ​"""​
​ 	​    List 'done' cards in db.​
​ 	​    """​
​ 	    ​with​ cards_db() ​as​ db:
​ 	        the_cards = db.list_done_cards()
​ 	        print_cards_list(the_cards)
```
This command calls an API method, list_done_cards(), and prints the results. The list_done_cards() API method really just needs to call list_cards() with a pre-filled state="done":

[ch13/cards_proj/src/cards/api.py](./cards_proj/src/cards/api.py?plain=1#L91-L93)
```python
​ 	​def​ ​list_done_cards​(self):
​ 	    ​"""Return the 'done' cards."""​
​ 	    done_cards = self.list_cards(state=​"done"​)
```
Now let’s add some tests for the API and CLI.

First, the API test:

[ch13/cards_proj/tests/api/test_list_done.py](./cards_proj/tests/api/test_list_done.py?plain=1#L1-L14)
```python
​ 	​import​ ​pytest​
​ 	
​ 	
​ 	@pytest.mark.num_cards(10)
​ 	​def​ ​test_list_done​(cards_db):
​ 	    cards_db.finish(3)
​ 	    cards_db.finish(5)
​ 	
​ 	    the_list = cards_db.list_done_cards()
​ 	
​ 	    ​assert​ len(the_list) == 2
​ 	    ​for​ card ​in​ the_list:
​ 	        ​assert​ card.id ​in​ (3, 5)
​ 	        ​assert​ card.state == ​"done"​
```

Here we set up a list of 10 cards and marked two as finished. The result of ``list_done_cards()`` should be a list of two cards with the correct index and with state set to ``"done"``. The ``@pytest.mark.num_cards(10)`` lets Faker generate the contents of the cards.

Now let’s add the CLI test:

[ch13/cards_proj/tests/cli/test_done.py](./cards_proj/tests/cli/test_done.py?plain=1#L1-L16)
```python
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
``` 
For the CLI test, we can’t use the Faker data, as we have to know exactly what the outcome is going to be. Instead, we just fill in a few cards and set state to ``"done"`` for a couple of them.

If we try to run these tests in the same virtual environment in which we were testing Cards before, they won’t work. We need to install the new version of Cards. Because we are editing the Cards source code, we’ll need to install it in editable mode. We’ll go ahead and install ``cards_proj`` in a new virtual environment.
## Installing Cards in Editable Mode
When developing both source and test code, it’s super handy to be able to modify the source code and immediately run the tests, without having to rebuild the package and reinstall it in our virtual environment. Installing the source code in editable mode is just the thing we need to accomplish this, and it’s a feature built in to both pip and Flit.

Let’s spin up a new virtual environment:
* In Unix or MacOS ：
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch13​
​ 	​$ ​​python3​​ ​​-m​​ ​​venv​​ ​​venv​
​ 	​$ ​​source​​ ​​venv/bin/activate​
​ 	(venv) $ pip install -U pip
​ 	​...​
​ 	Successfully installed pip-21.3.x
```
* In Windows ：
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch13​
​ 	​$ ​​python3​​ ​​-m​​ ​​venv​​ ​​venv​
​ 	​$ ​​​venv\Scripts\activate
​ 	(venv) $ pip install -U pip
​ 	​...​
​ 	Successfully installed pip-21.3.x
```
Now in our fresh virtual environment, we need to install the ``./cards_proj`` directory as a local editable package. For this to work, we need pip version 21.3.1 or above, so be sure to upgrade pip if it’s below 21.3.

Installing an editable package is as easy as ``pip install -e ./package_dir_name``. If we run ``pip install -e ./cards_proj`` we will have cards installed in editable mode. However, we also want to install all the necessary development tools like pytest, tox, etc.

We can install cards in editable mode and install all of our test tools all at once using optional dependencies.
```bash
​ 	$ pip install -e "./cards_proj/[test]"
```

This works because all of these dependencies have been defined in ``pyproject.toml``, in a ``optional-dependencies`` section:

[ch13/cards_proj/pyproject.toml](./cards_proj/pyproject.toml?plain=1#L25-L32)
```toml
​ 	​[project.optional-dependencies]​
​ 	test = [
​ 	    ​"pytest"​,
​ 	    ​"faker"​,
​ 	    ​"tox"​,
​ 	    ​"coverage"​,
​ 	    ​"pytest-cov"​,
​ 	]
```

Now let’s run the tests. We are using ```--tb=no``` to turn off tracebacks:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch13/cards_proj​
​ 	​$ ​​pytest​​ ​​--tb=no​
​ 	========================= test session starts ==========================
​ 	collected 55 items
​ 	
​ 	tests/api/test_add.py .....                                      [  9%]
​ 	​...​
​ 	tests/api/test_list_done.py .F                                   [ 49%]
​ 	​...​
​ 	tests/cli/test_done.py .F                                        [ 80%]
​ 	​...​
​ 	tests/cli/test_version.py .                                      [100%]
​ 	
​ 	======================= short test summary info ========================
​ 	FAILED tests/api/test_list_done.py::test_list_done - TypeError: objec...
​ 	FAILED tests/cli/test_done.py::test_done - AssertionError: assert '' ...
​ 	===================== 2 failed, 53 passed in 0.33s =====================
```
Awesome. There are a couple failures, which is just what we wanted. Now we can look at debugging.
## Debugging with pytest Flags
pytest includes quite a few command-line flags that are useful for debugging. We will be using some of these to debug our test failures.

Flags for selecting which tests to run, in which order, and when to stop:
* **-lf / --last-failed**: Runs just the tests that failed last
* **-ff / --failed-first**: Runs all the tests, starting with the last failed
* **-x / --exitfirst**: Stops the tests session after the first failure
* **--maxfail=num**: Stops the tests after num failures
* **-nf / --new-first**: Runs all the tests, ordered by file modification time
* **--sw / --stepwise**: Stops the tests at the first failure. Starts the tests at the last failure next time
* **--sw-skip / --stepwise-skip**: Same as --sw, but skips the first failure

Flags to control pytest output:
* **-v / --verbose**: Displays all the test names, passing or failing
* **--tb=[auto/long/short/line/native/no]**: Controls the traceback style
* **-l / --showlocals**: Displays local variables alongside the stacktrace

Flags to start a command-line debugger:
* **--pdb**: Starts an interactive debugging session at the point of failure
* **--trace**: Starts the pdb source-code debugger immediately when running each test
* **--pdbcls**: Uses alternatives to pdb, such as IPython’s debugger with ``--pdbcls=IPython.terminal.debugger:TerminalPdb``

For all of these descriptions, “failure” refers to a failed assertion or any other uncaught exception found in our source code or test code, including fixtures.

## Re-Running Failed Tests
Let’s start our debugging by making sure the tests fail when we run them again. We’ll use ``--lf`` to re-run the failures only, and ``--tb=no`` to hide the traceback, because we’re not ready for it yet:
```bash
​ 	​$ ​​pytest​​ ​​--lf​​ ​​--tb=no​
​ 	========================= test session starts ==========================
​ 	collected 27 items / 25 deselected / 2 selected
​ 	run-last-failure: re-run previous 2 failures (skipped 13 files)
​ 	
​ 	tests/api/test_list_done.py F                                    [ 50%]
​ 	tests/cli/test_done.py F                                         [100%]
​ 	
​ 	======================= short test summary info ========================
​ 	FAILED tests/api/test_list_done.py::test_list_done - TypeError: objec...
​ 	FAILED tests/cli/test_done.py::test_done - AssertionError: assert '' ...
​ 	=================== 2 failed, 25 deselected in 0.10s ===================
```

Great. We know we can reproduce the failure. We’ll start with debugging the first failure.

Let’s run just the first failing test, stop after the failure, and look at the traceback:
```bash

​ 	​$ ​​pytest​​ ​​--lf​​ ​​-x​
​ 	========================= test session starts ==========================
​ 	collected 27 items / 25 deselected / 2 selected
​ 	run-last-failure: re-run previous 2 failures (skipped 13 files)
​ 	
​ 	tests/api/test_list_done.py F
​ 	
​ 	=============================== FAILURES ===============================
​ 	____________________________ test_list_done ____________________________
​ 	
​ 	cards_db = <cards.api.CardsDB object at 0x7fabab5288b0>
​ 	
​ 	    @pytest.mark.num_cards(10)
​ 	    def test_list_done(cards_db):
​ 	        cards_db.finish(3)
​ 	        cards_db.finish(5)
​ 	
​ 	        the_list = cards_db.list_done_cards()
​ 	​>​​       ​​assert​​ ​​len(the_list)​​ ​​==​​ ​​2​
»	E       TypeError: object of type 'NoneType' has no len()
​ 	
​ 	tests/api/test_list_done.py:10: TypeError
​ 	======================= short test summary info ========================
​ 	FAILED tests/api/test_list_done.py::test_list_done - TypeError: objec...
​ 	!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!
​ 	=================== 1 failed, 25 deselected in 0.18s ===================
```
The error, ``TypeError: object of type ’NoneType’ has no len()`` is telling us that ``the_list`` is ``None``. That’s not good. We expect it to be a list of Card objects. Even if there are no “done” cards, it should be an empty list and not ``None``. Actually, that’s probably a good test to add, checking that everything works properly with no “done” cards. Focusing on the problem at hand, let’s get back to debugging.

Just to be sure we understand the problem, we can run the same test over again with ``-l/--showlocals``. We don’t need the full traceback again, so we can shorten it with ``--tb=short``:
```bash
​ 	​$ ​​pytest​​ ​​--lf​​ ​​-x​​ ​​-l​​ ​​--tb=short​
​ 	========================= test session starts ==========================
​ 	collected 27 items / 25 deselected / 2 selected
​ 	run-last-failure: re-run previous 2 failures (skipped 13 files)
​ 	
​ 	tests/api/test_list_done.py F
​ 	
​ 	=============================== FAILURES ===============================
​ 	____________________________ test_list_done ____________________________
​ 	tests/api/test_list_done.py:10: in test_list_done
​ 	    assert len(the_list) == 2
​ 	E   TypeError: object of type 'NoneType' has no len()
​ 	        cards_db   = <cards.api.CardsDB object at 0x7f884a4e8850>
»	        the_list   = None
​ 	======================= short test summary info ========================
​ 	FAILED tests/api/test_list_done.py::test_list_done - TypeError: objec...
​ 	!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!
​ 	=================== 1 failed, 25 deselected in 0.18s ===================
```

Yep. ``the_list = None``. The ``-l/--showlocals`` is often extremely helpful and sometimes good enough to debug a test failure completely. What’s more, the existence of ``-l/--showlocals`` has trained me to use lots of intermediate variables in tests. They come in handy when a test fails.

Now we know that in this circumstance, ``list_done_cards()`` is returning None. But we don’t know why. We’ll use pdb to debug inside ``list_done_cards()`` during the test.

## Debugging with pdb
[pdb](https://docs.python.org/3/library/pdb.html), which stands for “Python debugger,” is part of the Python standard library, so we don’t need to install anything to use it. We’ll get pdb up and running and then look at some of the most useful commands within pdb.

You can launch pdb from pytest in a few different ways:
* Add a ``breakpoint()`` call to either test code or application code. When a pytest run hits a ``breakpoint()`` function call, it will stop there and launch pdb.
* Use the ``--pdb`` flag. With ``--pdb``, pytest will stop at the point of failure. In our case, that will be at the ``assert len(the_list) == 2`` line.
* Use the ``--trace`` flag. With ``--trace``, pytest will stop at the beginning of each test.

For our purposes, combining ``--lf`` and ``--trace`` will work perfectly. The combo will tell pytest to re-run the failed tests and stop at the beginning of ``test_list_done()``, before the call to ``list_done_cards()``:
```bash

​ 	​$ ​​pytest​​ ​​--lf​​ ​​--trace​
​ 	========================= test session starts ==========================
​ 	collected 27 items / 25 deselected / 2 selected
​ 	run-last-failure: re-run previous 2 failures (skipped 13 files)
​ 	
​ 	tests/api/test_list_done.py
​ 	​>>>​​>>>>>>>>>>>>>​​ ​​PDB​​ ​​runcall​​ ​​(IO-capturing​​ ​​turned​​ ​​off)​​ ​​>>>>>>>>>>>>>>>>>​
​ 	​>​​ ​​/path/to/code/ch13/cards_proj/tests/api/test_list_done.py(5)test_list_done()​
​ 	​->​​ ​​cards_db.finish(3)​
​ 	(Pdb)
```

Following are the common commands recognized by pdb. The full list is in the pdb [documentation](https://docs.python.org/3/library/pdb.html#debugger-commands).

Meta commands:
* ``h(elp)``: Prints a list of commands
* ``h(elp) command``: Prints help on a command
* ``q(uit)``: Exits pdb

Seeing where you are:
* ``l(ist)`` : Lists 11 lines around the current line. Using it again lists the next 11 lines, and so on.
* ``l(ist) .`` : The same as above, but with a dot. Lists 11 lines around the current line. Handy if you’ve use l(list) a few times and have lost your current position
* ``l(ist) first, last``: Lists a specific set of lines
* ``ll`` : Lists all source code for the current function
* ``w(here)``: Prints the stack trace

Looking at values:
* ``p(rint) expr``: Evaluates ``expr`` and prints the value
* ``pp expr``: Same as ``p(rint) expr`` but uses pretty-print from the pprint module. Great for structures
* ``a(rgs)``: Prints the argument list of the current function

Execution commands:
* ``s(tep)``: Executes the current line and steps to the next line in your source code even if it’s inside a function
* ``n(ext)``: Executes the current line and steps to the next line in the current function
* ``r(eturn)``: Continues until the current function returns
* ``c(ontinue)``: Continues until the next breakpoint. When used with ``--trace``, continues until the start of the next test
* ``unt(il) lineno``: Continues until the given line number

Continuing on with debugging our tests, we’ll use ll to list the current function:
```bash
​ 	(Pdb) ll
​ 	  3     @pytest.mark.num_cards(10)
​ 	  4     def test_list_done(cards_db):
​ 	  5  ->     cards_db.finish(3)
​ 	  6         cards_db.finish(5)
​ 	  7
​ 	  8         the_list = cards_db.list_done_cards()
​ 	  9
​ 	 10         assert len(the_list) == 2
​ 	 11         for card in the_list:
​ 	 12             assert card.id in (3, 5)
​ 	 13             assert card.state == "done"
```

The -> shows us the current line, before it’s been run.

We can use ``until 8`` to break right before we call list_done_cards(), like this:
```bash
​ 	(Pdb) until 8
 	​>​​ ​​/path/to/code/ch13/cards_proj/tests/api/test_list_done.py(8)test_list_done()​
​ 	​->​​ ​​the_list​​ ​​=​​ ​​cards_db.list_done_cards()
```
And ``step`` to get us into the function:
```bash
​ 	(Pdb) step
​ 	--Call--
​ 	​>​​ ​​/path/to/code/ch13/cards_proj/src/cards/api.py(82)list_done_cards()​
​ 	​->​​ ​​def​​ ​​list_done_cards(self):​
```
Let’s use ``ll`` again to see the whole function:
```bash
​ 	(Pdb) ll
​ 	 82  ->     def list_done_cards(self):
​ 	 83             """Return the 'done' cards."""
​ 	 84             done_cards = self.list_cards(state='done')
```
Now let’s continue until just before this function returns:
```bash
​ 	(Pdb) return
​ 	--Return--
​ 	​>​​ ​​/path/to/code/ch13/cards_proj/src/cards/api.py(84)list_done_cards()->None​
​ 	​->​​ ​​done_cards​​ ​​=​​ ​​self.list_cards(state=​​'done'​​)​
​ 	(Pdb) ll
​ 	 82         def list_done_cards(self):
​ 	 83             """Return the 'done' cards."""
​ 	 84  ->         done_cards = self.list_cards(state='done')
```
We can look at the value of ``done_cards`` with either ``p`` or ``pp``:
```bash
​ 	(Pdb) pp done_cards
​ 	[Card(summary='Line for PM identify decade.', owner='Russell', state='done', id=3),
​ 	 Card(summary='Director season industry the describe.', owner='Cody', state='done', id=5)]
```
This looks fine, but I think I see the problem. If we continue out to the calling test and check the return value, we can make doubly sure:
```bash
​ 	(Pdb) step
​ 	​>​​ ​​/path/to/code/ch13/cards_proj/tests/api/test_list_done.py(10)test_list_done()​
​ 	​->​​ ​​assert​​ ​​len(the_list)​​ ​​==​​ ​​2​
​ 	(Pdb) ll
​ 	  3     @pytest.mark.num_cards(10)
​ 	  4     def test_list_done(cards_db):
​ 	  5         cards_db.finish(3)
​ 	  6         cards_db.finish(5)
​ 	  7
​ 	  8         the_list = cards_db.list_done_cards()
​ 	  9
​ 	 10  ->     assert len(the_list) == 2
​ 	 11         for card in the_list:
​ 	 12             assert card.id in (3, 5)
​ 	 13             assert card.state == "done"
​ 	(Pdb) pp the_list
​ 	None
```

Pretty clear now. We had the correct list in the ``done_cards`` variable within ``list_done_cards()``. However, that value isn’t returned. Because the default return value in Python is ``None`` if there isn’t a ``return`` statement, that’s the value that gets assigned to ``the_list`` in ``test_list_done()``.

If we stop the debugger, add a ``return done_cards`` to ``list_done_cards()``, and re-run the failed test, we can see if that fixes it:
```bash
​ 	(Pdb) exit
​ 	!!!!!!!!!!!!!!! _pytest.outcomes.Exit: Quitting debugger !!!!!!!!!!!!!!!
​ 	================== 25 deselected in 521.22s (0:08:41) ==================
​ 	​$ ​​pytest​​ ​​--lf​​ ​​-x​​ ​​-v​​ ​​--tb=no​
​ 	========================= test session starts ==========================
​ 	collected 27 items / 25 deselected / 2 selected
​ 	run-last-failure: re-run previous 2 failures (skipped 13 files)
​ 	
​ 	tests/api/test_list_done.py::test_list_done PASSED               [ 50%]
​ 	tests/cli/test_done.py::test_done FAILED                         [100%]
​ 	
​ 	======================= short test summary info ========================
​ 	FAILED tests/cli/test_done.py::test_done - AssertionError: assert '  ...
​ 	!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!
​ 	============== 1 failed, 1 passed, 25 deselected in 0.10s ==============
```
Wonderful. We fixed one bug. One more to go.
## Combining pdb and tox
To debug the next test failure, we’re going to combine tox and pdb. For this to work, we have to make sure we can pass arguments through tox to pytest. This is done with tox’s ``{posargs}`` feature, which was discussed in [​Passing pytest Parameters Through tox](../ch11/README.md#passing-pytest-parameters-through-tox)​.

We’ve already got that set up in our tox.ini for Cards:

[ch13/cards_proj/tox.ini](./cards_proj/tox.ini)
```ini
​ 	​[tox]​
​ 	envlist = ​py39, py310​
​ 	isolated_build = ​True​
​ 	skip_missing_interpreters = ​True​
​ 	
​ 	​[testenv]​
​ 	deps =
​ 	  ​pytest​
​ 	  ​faker​
​ 	  ​pytest-cov​
»	commands = ​pytest --cov=cards --cov=tests --cov-fail-under=100 {posargs}​
```

We’d like to run the Python 3.10 environment, and start the debugger at the test failure. We could run it once with ``-e py310``, then use ``-e py310 -- --lf --trace`` to stop at the entry point of the first failing test.

Instead, let’s just run it once and stop at the failure point with ``-e py310 -- --pdb --no-cov. (--no-cov`` is used to turn off the coverage report.)
```bash


​ 	​$ ​​tox​​ ​​-e​​ ​​py310​​ ​​--​​ ​​--pdb​​ ​​--no-cov​
​ 	​...​
​ 	py310 run-test: commands[0] | pytest --cov=cards --cov=tests
​ 	--cov-fail-under=100 --pdb --no-cov
​ 	========================= test session starts ==========================
​ 	​...​
​ 	collected 53 items
​ 	
​ 	tests/api/test_add.py .....                                      [  9%]
​ 	tests/api/test_config.py .                                       [ 11%]
​ 	​...​
​ 	tests/cli/test_delete.py .                                       [ 77%]
​ 	tests/cli/test_done.py F
​ 	​>>>​​>>>>>>>>>>>>>>>>>>>>>>>>>>>​​ ​​traceback​​ ​​>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>​
​ 	
​ 	​...​
​ 	​>​​       ​​assert​​ ​​output​​ ​​==​​ ​​expected​
​ 	​...​
​ 	tests/cli/test_done.py:15: AssertionError
​ 	​>>>​​>>>>>>>>>>>>>>>>>>>>>>>>>>​​ ​​entering​​ ​​PDB​​ ​​>>>>>>>>>>>>>>>>>>>>>>>>>>>>>​
​ 	
​ 	​>>>​​>>>>>>>>>>>​​ ​​PDB​​ ​​post_mortem​​ ​​(IO-capturing​​ ​​turned​​ ​​off)​​ ​​>>>>>>>>>>>>>>>​
​ 	​>​​ ​​/path/to/code/ch13/cards_proj/tests/cli/test_done.py(15)test_done()​
​ 	​->​​ ​​assert​​ ​​output​​ ​​==​​ ​​expected​
​ 	(Pdb) ll
​ 	 10     def test_done(cards_db, cards_cli):
​ 	 11         cards_db.add_card(cards.Card("some task", state="done"))
​ 	 12         cards_db.add_card(cards.Card("another"))
​ 	 13         cards_db.add_card(cards.Card("a third", state="done"))
​ 	 14         output = cards_cli("done")
​ 	 15  ->     assert output == expected
```
That drops us into pdb, right at the assertion that failed.

We can use ``pp`` to look at the ``output`` and ``expected`` variables:
```bash

​ 	(Pdb) pp output
»	('                                  \n'
​ 	 '  ID   state   owner   summary    \n'
​ 	 ' ──────────────────────────────── \n'
​ 	 '  1    done            some task  \n'
​ 	 '  3    done            a third')
​ 	(Pdb) pp expected
»	('\n'
​ 	 '  ID   state   owner   summary    \n'
​ 	 ' ──────────────────────────────── \n'
​ 	 '  1    done            some task  \n'
​ 	 '  3    done            a third')
```

Now we can see the problem. The expected output starts with a line containing a single new line character, ``’\n’``. The actual output contains a bunch of spaces before the new line. This problem would be difficult to spot with the traceback only, or even in an IDE. With pdb, it’s not too hard to spot.

We can add those spaces to the test and re-run the tox environment with that one test failure:
```bash
   ​$ ​​tox​​ ​​-e​​ ​​py310​​ ​​--​​ ​​--lf​​ ​​--tb=no​​ ​​--no-cov​​  -v​
​ 	​...​
​ 	py310 run-test: commands[0] | pytest --cov=cards --cov=tests
​ 	 --cov-fail-under=100 --lf --tb=no --no-cov -v
​ 	========================= test session starts ==========================
​ 	​...​
​ 	
​ 	tests/cli/test_done.py::test_done PASSED                         [100%]
​ 	
​ 	=================== 1 passed, 41 deselected in 0.11s ===================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
And just for good measure, re-run the whole thing:
```bash
​ 	​$ ​​tox​
​ 	​...​
​ 	Required test coverage of 100% reached. Total coverage: 100.00%
​ 	
​ 	========================== 53 passed in 0.53s ==========================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
Woohoo! Defects fixed.
## Review
We covered a lot of techniques for debugging Python packages with command-line flags, pdb, and tox:
* We installed an editable version of Cards with ``pip install -e ./cards_proj``.
* We used many pytest flags for debugging. There’s list of useful flags at [​Debugging with pytest Flags](#debugging-with-pytest-flags).
* We used pdb to debug the tests. A subset of pdb commands is at [​Debugging with pdb](#debugging-with-pdb)​.
* We combined tox, pytest, and pdb to debug a failing test within a tox environment.
## Exercises
The code files included in the code download for this chapter don’t have the fixes. They just have the broken code. Even if you plan to do most of your debugging with an IDE, I encourage you to try the debugging techniques in this chapter to help you understand how to use the flags and pdb commands.
1. Create a new virtual environment and install Cards in editable mode.
2. Run pytest and make sure you see the same failures listed in the chapter.
3. Use ``--lf`` and ``--lf -x`` to see how they work.
4. Try ``--stepwise`` and ``--stepwise-skip``. Run them both a few times. How are they different than ``--lf`` and ``--lf -x``?
5. Use ``--pdb`` to open pdb at a test failure.
6. Use ``--lf --trace`` to open pdb at the start of the first failing test.
7. Fix both bugs and verify with a clean test run.
8. Add ``breakpoint()`` somewhere in the source code or test code and run pytest with neither ``--pdb`` or ``--trace``.
9. (Bonus) Break something again and try IPython for debugging. ([IPython](https://ipython.readthedocs.io/en/stable/index.html) is part of the [Jupyter](https://jupyter.org) project. Please see their respective documentation for more information.)
   * Install IPython with ``pip install ipython``.
   * You can run it with:
      * ``pytest --lf --trace --pdbcls=IPython.terminal.debugger:TerminalPdb``
      * ``pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb``
      * Put ``breakpoint()`` somewhere in the code and run ``pytest --pdbcls=IPython.terminal.debugger:TerminalPdb``