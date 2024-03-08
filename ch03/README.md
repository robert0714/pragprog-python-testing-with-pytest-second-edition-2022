# pytest Fixtures
 Fixtures are functions that are run by pytest **before** (and sometimes **after**) the actual test functions.
## Getting Started with Fixtures
Here’s a [simple fixture](./test_fixtures.py?plain=1#L6-L12) that returns a number:
```python
import pytest

@pytest.fixture()
def some_data():
    """Return answer to ultimate question."""
    return 42
def test_some_data(some_data):
    """Use fixture return value in a test."""
    assert some_data == 42
```
The ``@pytest.fixture()`` decorator is used to tell pytest that a function is a fixture. When you include the fixture name in the parameter list of a test function, pytest knows to run it before running the test. Fixtures can do work, and can also return data to the test function.

You don’t need to have a complete understanding of Python decorators to use the decorators included with pytest. pytest uses decorators to add functionality and features to other functions. In this case, ``pytest.fixture()`` is decorating the ``some_data()`` function. The test, ``test_some_data()``, has the name of the fixture, some_data, as a parameter. pytest will see this and look for a fixture with this name.

The term **fixture** has many meanings in the programming and test community, and even in the Python community. I use “fixture,” “fixture function,” and “fixture method” interchangeably to refer to the ``@pytest.fixture()`` decorated functions discussed in this chapter. Fixture can also be used to refer to the resource that is being set up by the fixture functions. Fixture functions often set up or retrieve some data that the test can work with. Sometimes this data is considered a fixture. For example, the Django community often uses fixture to mean some initial data that gets loaded into a database at the start of an application.

Regardless of other meanings, in pytest and in this book, test fixtures refer to the mechanism pytest provides to allow the separation of “getting ready for” and “cleaning up after” code from your test functions.

pytest treats exceptions differently during fixtures compared to during a test function. An exception (or **assert** failure or call to **pytest.fail()**) that happens during the test code proper results in a “Fail” result. However, during a fixture, the test function is reported as “Error.” This distinction is helpful when debugging why a test didn’t pass. If a test results in “Fail,” the failure is somewhere in the test function (or something the function called). If a test results in “Error,” the failure is somewhere in a fixture.

pytest fixtures are one of the unique core features that make pytest stand out above other test frameworks, and are the reason why many people switch to and stay with pytest. There are a lot of features and nuances about fixtures. Once you get a good mental model of how they work, they will seem easy to you. However, you have to play with them a while to get there, so let’s do that next.

## Using Fixtures for Setup and Teardown
Fixtures are going to help us a lot with testing the Cards application. The Cards application is designed with an API that does most of the work and logic, and a thin CLI. Especially because the user interface is rather thin on logic, focusing most of our testing on the API will give us the most bang for our buck. The Cards application also uses a database, and dealing with the database is where fixtures are going to help out a lot.
> Make Sure Cards Is Installed
>> Examples in this chapter require having the Cards application installed. If you haven’t already installed the Cards application, be sure to install it with ``cd code; pip install ./cards_proj``. See [​Installing the Sample Application](./../ch02/README.md#installing-the-sample-application)  for more information.

Let’s start by writing some tests for the ``count()`` method that supports the ``count`` functionality. As a reminder, let’s play with ``count`` on the command line:
```bash
​ 	​$ ​​cards​​ ​​count​
​ 	0
​ 	​$ ​​cards​​ ​​add​​ ​​first​​ ​​item​
​ 	​$ ​​cards​​ ​​add​​ ​​second​​ ​​item​
​ 	​$ ​​cards​​ ​​count​
​ 	2
```
An initial test, checking that the count starts at zero, [might look like this](./test_count.py?plain=1#L1-L18):
```python
import pytest

@pytest.fixture()
def cards_db():
    with TemporaryDirectory() as db_dir:
        db_path = Path(db_dir)
        db = cards.CardsDB(db_path)
        yield db
        db.close()

def test_empty(cards_db):
    assert cards_db.count() == 0
```
Right off the bat we can see that the test function itself is way easier to read, as we’ve pushed all the database initialization into a fixture called cards_db.

The cards_db fixture is “setting up” for the test by getting the database ready. It’s then yield-ing the database object. That’s when the test gets to run. And then after the test runs, it closes the database.

Fixture functions run before the tests that use them. If there is a yield in the function, it stops there, passes control to the tests, and picks up on the next line after the tests are done. The code above the yield is “setup” and the code after yield is “teardown.” The code after the yield, the teardown, is guaranteed to run regardless of what happens during the tests.

In our example, the yield happens within a context manager with block for the temporary directory. That directory stays around while the fixture is in use and the tests run. After the test is done, control passes back to the fixture, the db.close() can run, and then the with block can complete and clean up the directory.

Remember: pytest looks at the specific name of the arguments to our test and then looks for a fixture with the same name. We never call fixture functions directly. pytest does that for us.

You can use fixtures in multiple tests. [Here’s another one](./test_count.py?plain=1#L22-L25):
```python
def test_two(cards_db):
    cards_db.add_card(cards.Card("first"))
    cards_db.add_card(cards.Card("second"))
    assert cards_db.count() == 2
```
``test_two()`` uses the same ``cards_db`` fixture. This time, we take the empty database and add two cards before checking the count. We can now use ``cards_db`` for any test that needs a configured database to run. The individual tests, such as ``test_empty()`` and ``test_two()`` can be kept smaller and focus on what we are testing, and not the setup and teardown bits.

The fixture and test function are separate functions. Carefully naming your fixtures to reflect the work being done in the fixture or the object returned from the fixture, or both, will help with readability.

While writing and debugging test functions, it’s frequently helpful to visualize when the setup and teardown portions of fixtures run with respect the tests using them. The next section describes ``--setup-show`` to help with this visualization.
## Tracing Fixture Execution with –setup-show
Now that we have two tests using the same fixture, it would be interesting to know exactly in what order everything is getting called.

Fortunately, pytest provides the command-line flag, ``--setup-show``, which shows us the order of operations of tests and fixtures, including the setup and teardown phases of the fixtures:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch03​
​ 	​$ ​​pytest​​ ​​--setup-show​​ ​​test_count.py
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_count.py
        SETUP    F cards_db
        ch03/test_count.py::test_empty (fixtures used: cards_db).
        TEARDOWN F cards_db
        SETUP    F cards_db
        ch03/test_count.py::test_two (fixtures used: cards_db).
        TEARDOWN F cards_db

==================================================================== 2 passed in 0.51s =====================================================================
```
We can see that our test runs, surrounded by the ``SETUP`` and ``TEARDOWN`` portions of the ``cards_db`` fixture. The F in front of the fixture name indicates that the fixture is using function scope, meaning the fixture is called before each test function that uses it, and torn down after each function that uses it. Let’s take a look at scope next.

## Specifying Fixture Scope
Each fixture has a specific scope, which **defines the order of when the setup and teardown run** relative to running of all the test function using the fixture. The scope dictates how often the setup and teardown get run when it’s used by multiple test functions.

The default scope for fixtures is ``function`` scope. That means the setup portion of the fixture will run before each test that needs it runs. Likewise, the teardown portion runs after the test is done, for each test.

However, there may be times when you don’t want that to happen. Perhaps setting up and connecting to the database is time-consuming, or you are generating large sets of data, or you are retrieving data from a server or a slow device. Really, you can do anything you want within a fixture, and some of that may be slow.

I could show you an example where I put a ``time.sleep(1)`` statement in the fixture when we are connecting to the database to simulate a slow resource, but I think it suffices that you imagine it. So, if we want to avoid that slow connection twice in our example, or imagine 100 seconds for a hundred tests, we can change the scope such that the slow part happens once for multiple tests.

Let’s change the scope of our fixture so the database is only opened once, and then talk about different scopes.

It’s a one-line change, adding ``scope="module"`` [to the fixture decorator](./test_mod_scope.py?plain=1#L7-L13):
```python
@pytest.fixture(scope="module")
def cards_db():
    with TemporaryDirectory() as db_dir:
        db_path = Path(db_dir)
        db = cards.CardsDB(db_path)
        yield db
        db.close()
```
Now let’s run it again:
```bash
	​$ ​​pytest​​ ​​--setup-show​​ ​​test_mod_scope.py
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_mod_scope.py
    SETUP    M cards_db
        ch03/test_mod_scope.py::test_empty (fixtures used: cards_db).
        ch03/test_mod_scope.py::test_non_empty (fixtures used: cards_db).
    TEARDOWN M cards_db

==================================================================== 2 passed in 0.14s =====================================================================    
```
Whew! We saved that imaginary one second of setup time for the second test function. The change to module scope allows any test in this module that uses the ``cards_db`` fixture to share the same instance of it and not incur extra setup/teardown time.

The fixture decorator ``scope`` parameter allows more than ``function`` and ``module``. There’s also ``class``, ``package``, and ``session``. The default scope is ``function``.

Here’s a rundown of each scope value:
* **scope=’function’**  
  Run once per test function. The setup portion is run before each test using the fixture. The teardown portion is run after each test using the fixture. This is the default scope used when no scope parameter is specified.

* **scope=’class’**  
  Run once per test class, regardless of how many test methods are in the class.

* **scope=’module’**  
  Run once per module, regardless of how many test functions or methods or other fixtures in the module use it.

* **scope=’package’**  
  Run once per package, or test directory, regardless of how many test functions or methods or other fixtures in the package use it.

* **scope=’session’**  
  Run once per session. All test methods and functions using a fixture of session scope share one setup and teardown call.

Scope is defined with the fixture. I know this is obvious from the code, but it’s an important point to make sure you fully grok. The scope is set at the definition of a fixture, and not at the place where it’s called. The test functions that use a fixture don’t control how often a fixture is set up and torn down.

With a fixture defined within a test module, the **session** and **package** scopes act just like module scope. In order to make use of these other scopes, we need to put them in a **conftest.py** file.
## Sharing Fixtures through conftest.py
You can put fixtures into individual test files, but to share fixtures among multiple test files, you need to use a [**conftest.py**](./a/conftest.py) file either in the same directory as the test file that’s using it or in some parent directory. The [**conftest.py**](./a/conftest.py) file is also optional. It is considered by pytest as a “local plugin” and can contain hook functions and fixtures.

Let’s start by moving the cards_db fixture out of [**test_count.py**](./a/test_count.py) and into a conftest.py file in the same directory:
* [**conftest.py**](./a/conftest.py)
* [**test_count.py**](./a/test_count.py)
And yep, it still works:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch3/a/​
​ 	​$ ​​pytest​​ ​​--setup-show​​ ​​test_count.py
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_count.py
SETUP    S cards_db
        ch03/a/test_count.py::test_empty (fixtures used: cards_db).
        ch03/a/test_count.py::test_two (fixtures used: cards_db).
TEARDOWN S cards_db

==================================================================== 2 passed in 0.04s =====================================================================
```
Fixtures can only depend on other fixtures of their same scope or wider. So a function-scope fixture can depend on other function-scope fixtures (the default, and used in the Cards project so far). A function-scope fixture can also depend on class-, module-, and session-scope fixtures, but you can’t go in the reverse order.

> Don’t Import [**conftest.py**](./a/conftest.py)
>> ⚠ 	Although [**conftest.py**](./a/conftest.py) is a Python module, it should not be imported by test files. The [**conftest.py**](./a/conftest.py) file gets read by pytest automatically, so you don’t have ``import conftest`` anywhere.

## Finding Where Fixtures Are Defined
We’ve moved a fixture out of the test module and into a [**conftest.py**](./a/conftest.py) file. We can have [**conftest.py**](./a/conftest.py) files at really every level of our test directory. Tests can use any fixture that is in the same test module as a test function, or in a [**conftest.py**](./a/conftest.py) file in the same directory, or in any level of parent directory up to the root of the tests.

That brings up a problem if we can’t remember where a particular fixture is located and we want to see the source code. Of course, pytest has our back. Just use ``--fixtures`` and we are good to go.

Let’s first try it:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch3/a/​
​ 	​$ ​​pytest​​ ​​--fixtures​​ ​​-v
(ommitted​...)
-------------------------------------------------------------- fixtures defined from conftest --------------------------------------------------------------
cards_db [session scope] -- conftest.py:8
    CardsDB object connected to a temporary database
================================================================== no tests ran in 0.07s ===================================================================
```
pytest shows us a list of all available fixtures our test can use. This list includes a bunch of builtin fixtures that we’ll look at in the next chapter, as well as those provided by plugins. The fixtures found in [**conftest.py**](./a/conftest.py) files are at the bottom. If you supply a directory, pytest will list the fixtures available to tests in that directory. If you supply a test file name, pytest will include those defined in test modules as well.

pytest also includes the first line of the docstring from the fixture, if you’ve defined one, and the file and line number where the fixture is defined. It will also include the path if it’s not in your current directory.

Adding -v will include the entire docstring. Note that for pytest 6.x, we have to use -v to get the path and line numbers. Those were added to ``--fixturues`` without verbose for pytest 7.

You can also use ``--fixtures-per-test`` to see what fixtures are used by each test and where the fixtures are defined:
```bash
$ ​​pytest​​ ​​--fixtures-per-test​​ ​​test_count.py::test_empty
============================================================================== test session starts ===============================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 1 item

-------------------------------------------------------------------------- fixtures used by test_empty ---------------------------------------------------------------------------
------------------------------------------------------------------------------- (test_count.py:5) --------------------------------------------------------------------------------
cards_db -- conftest.py:8
    CardsDB object connected to a temporary database

============================================================================= no tests ran in 0.02s ==============================================================================
```
In this example we’ve specified an individual test, ``test_count.py::test_empty``. However, the flag works for files or directories as well. Armed with ``--fixtures`` and ``--fixtures-per-test``, you’ll never again wonder where a fixture is defined.

## Using Multiple Fixture Levels
There’s a little bit of a problem with our test code right now. The problem is the tests both depend on the database being empty to start with, but they use the same database instance in the module-scope and session-scope versions.

The problem becomes very clear if we add a [third test](./a/test_three.py?plain=1#L4-L8):

It works fine by itself, but not when it’s run after ``test_count.py::test_two``:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch3/a/​
​ 	​$ pytest​​ ​​-v​​ ​​test_three.py
============================================================================== test session starts ===============================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 1 item

test_three.py::test_three PASSED                                                                                                                                            [100%]

=============================================================================== 1 passed in 0.06s ================================================================================

​ 	​$ pytest​​ ​​-v​​ ​​--tb=line test_count.py test_three.py
============================================================================== test session starts ==============================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 3 items

test_count.py::test_empty PASSED                                                                                                                                           [ 33%]
test_count.py::test_two PASSED                                                                                                                                             [ 66%]
test_three.py::test_three FAILED                                                                                                                                           [100%]

=================================================================================== FAILURES ====================================================================================
E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022\ch03\a\test_three.py:8: assert 5 == 3
============================================================================ short test summary info ============================================================================
FAILED test_three.py::test_three - assert 5 == 3
========================================================================== 1 failed, 2 passed in 0.09s ==========================================================================
```
There are five elements in the database because the previous test added two items before ``test_three`` ran. There’s a time-honored rule of thumb that says tests shouldn’t rely on the run order. And clearly, this does. ``test_three`` passes just fine if we run it by itself, but fails if it is run after ``test_two``.

If we still want to try to stick with one open database, but start all the tests with zero elements in the database, we can do that by adding [another fixture](./b/conftest.py?plain=1#L7-L21):
```python
@pytest.fixture(scope="session")
def db():
    """CardsDB object connected to a temporary database"""
    with TemporaryDirectory() as db_dir:
        db_path = Path(db_dir)
        db_ = cards.CardsDB(db_path)
        yield db_
        db_.close()


@pytest.fixture(scope="function")
def cards_db(db):
    """CardsDB object that's empty"""
    db.delete_all()
    return db
```
I’ve renamed the old ``cards_db`` to ``db`` and made it session scope.

The ``cards_db`` fixture has ``db`` named in its parameter list, which means it depends on the ``db`` fixture. Also, ``cards_db`` is function scoped, which is a more narrow scope than ``db``. When fixtures depend on other fixtures, they can only use fixtures that have equal or wider scope.

Let’s see if it works:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch3/b/​
​ 	​$ ​​pytest​​ ​​--setup-show
============================================================================== test session starts ==============================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 3 items

test_count.py
SETUP    S db
        SETUP    F cards_db (fixtures used: db)
        ch03/b/test_count.py::test_empty (fixtures used: cards_db, db).
        TEARDOWN F cards_db
        SETUP    F cards_db (fixtures used: db)
        ch03/b/test_count.py::test_two (fixtures used: cards_db, db).
        TEARDOWN F cards_db
test_three.py
        SETUP    F cards_db (fixtures used: db)
        ch03/b/test_three.py::test_three (fixtures used: cards_db, db).
        TEARDOWN F cards_db
TEARDOWN S db

=============================================================================== 3 passed in 0.10s ===============================================================================
```
We can see that the setup for **db** happens first, and has session scope (from the **S**). The setup for **cards_db** happens next, and before each test function call, and has function scope (from the **F**). Also, all three tests pass.

Using multiple stage fixtures like this can provide some incredible speed benefits and maintain test order independence.

## Using Multiple Fixtures per Test or Fixture
Another way we can use multiple fixtures is just to use more than one in either a function or a fixture. As an example, we can put some pre-canned tasks together to test with as [a fixture](./c/conftest.py?plain=1#L24-L32):
```python
@pytest.fixture(scope="session")
def some_cards():
    """List of different Card objects"""
    return [
        cards.Card("write book", "Brian", "done"),
        cards.Card("edit book", "Katie", "done"),
        cards.Card("write 2nd edition", "Brian", "todo"),
        cards.Card("edit 2nd edition", "Katie", "todo"),
    ]
```
Then we can use both **empty_db** and **some_cards** in [a test](./c/test_some.py?plain=1#L1-L5):
```python
def test_add_some(cards_db, some_cards):
    expected_count = len(some_cards)
    for c in some_cards:
        cards_db.add_card(c)
    assert cards_db.count() == expected_count
```
Fixtures can also use multiple other [fixture](./c/conftest.py?plain=1#L35-L40):
```python
@pytest.fixture(scope="function")
def non_empty_db(cards_db, some_cards):
    """CardsDB object that's been populated with 'some_cards'"""
    for c in some_cards:
        cards_db.add_card(c)
    return cards_db
```
The fixture **non_empty_db** has to be function scope because it uses **cards_db**, which is function scope. If you try to make **non_empty_db** module scope or wider, pytest will throw an error. Remember that if you don’t specify a scope, you get function-scope fixtures.

And now, [tests that need a database with stuff in it can do that easily](./c/test_some.py?plain=1#L8-L9):
```python
def test_non_empty(non_empty_db):
    assert non_empty_db.count() > 0
```
We’ve discussed how different fixture scopes work and how to use different scopes in different fixtures to our advantage. However, there may be times where you need a scope to be determined at runtime. That’s possible with dynamic scoping.

## Deciding Fixture Scope Dynamically
Let’s say we have the fixture setup as we do now, with ``db`` at session scope and ``cards_db`` at function scope, but we’re worried about it. The ``cards_db`` fixture is empty because it calls ``delete_all()``. But what if we don’t completely trust that ``delete_all()`` function yet, and want to put in place some way to completely set up the database for each test function?

We can do this by dynamically deciding the scope of the ``db`` [fixture](./d/conftest.py?plain=1#L23-L30) at runtime. First, we change the scope of ``db``:
```python
@pytest.fixture(scope=db_scope)
def db():
    """CardsDB object connected to a temporary database"""
    with TemporaryDirectory() as db_dir:
        db_path = Path(db_dir)
        db_ = cards.CardsDB(db_path)
        yield db_
        db_.close()
```
Instead of a specific scope, we’ve put in a function name, ``db_scope``. So we also have to write that [function](./d/conftest.py?plain=1#L16-L19):
```python
def db_scope(fixture_name, config):
    if config.getoption("--func-db", None):
        return "function"
    return "session"
```
There are many ways we could have figured out which scope to use, but in this case, I chose to depend on a [new command-line flag, ``--func-db``](./d/conftest.py?plain=1#L7-L13). In order to allow pytest to allow us to use this new flag, we need to write a hook function (which I’ll cover in more depth in Chapter 15, [​Building Plugins](../ch15/README.md)​):
```python
def pytest_addoption(parser):
    parser.addoption(
        "--func-db",
        action="store_true",
        default=False,
        help="new db for each test",
    )
```
After all that, the default behavior is the same as before, with session-scope ``db``:
```bash
​ 	​$ ​​pytest​​ ​​--setup-show​​ ​​test_count.py
================================================= test session starts =================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: D:\Data\workspaces\tmp\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_count.py
SETUP    S db
        SETUP    F cards_db (fixtures used: db)
        ch03/d/test_count.py::test_empty (fixtures used: cards_db, db).
        TEARDOWN F cards_db
        SETUP    F cards_db (fixtures used: db)
        ch03/d/test_count.py::test_two (fixtures used: cards_db, db).
        TEARDOWN F cards_db
TEARDOWN S db

================================================== 2 passed in 0.05s ==================================================
```
But when we use the new flag, we get a function-scope ``db`` fixture:
```bash
​ 	​$ ​​pytest​​ ​​​--func-db​​ ​​test_count.py
=================================================== test session starts ====================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: D:\Data\workspaces\tmp\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_count.py ..                                                                                                      [100%]

==================================================== 2 passed in 0.05s =====================================================
```
The database is now set up before each test function, and torn down afterwards.

## Using autouse for Fixtures That Always Get Used
So far in this chapter, all of the fixtures used by tests were named by the tests or another fixture in a parameter list. However, you can use ``autouse=True`` to get a fixture to run all of the time. This works well for code you want to run at certain times, but tests don’t really depend on any system state or data from the fixture.

Here’s a rather contrived [example](./test_autouse.py):
```python
import pytest
import time


@pytest.fixture(autouse=True, scope="session")
def footer_session_scope():
    """Report the time at the end of a session."""
    yield
    now = time.time()
    print("--")
    print(
        "finished : {}".format(
            time.strftime("%d %b %X", time.localtime(now))
        )
    )
    print("-----------------")


@pytest.fixture(autouse=True)
def footer_function_scope():
    """Report test durations after each function."""
    start = time.time()
    yield
    stop = time.time()
    delta = stop - start
    print("\ntest duration : {:0.3} seconds".format(delta))


def test_1():
    """Simulate long-ish running test."""
    time.sleep(1)


def test_2():
    """Simulate slightly longer test."""
    time.sleep(1.23)

```
We want to add test times after each test, and the date and current time at the end of the session. Here’s what these look like:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch03​
​ 	​$ ​​pytest​​ ​​-v​​ ​​-s​​ ​​test_autouse.py
=================================================== test session starts ====================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- d:\anaconda_envs_dirs\myenv\python.exe
cachedir: .pytest_cache
rootdir: D:\Data\workspaces\tmp\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_autouse.py::test_1 PASSED
test duration : 1.01 seconds

test_autouse.py::test_2 PASSED
test duration : 1.25 seconds
--
finished : 06 Mar 22:19:25
-----------------


==================================================== 2 passed in 2.28s =====================================================
```
I used the ``-s`` flag in this example. It’s a shortcut flag for ``--capture=no`` that tells pytest to turn off output capture. I used it because the new fixtures have print functions in them, and I wanted to see the output. Without turning off output capture, pytest only prints the output of tests that fail.

The ``autouse`` feature is good to have around. But it’s more of an exception than a rule. Opt for named fixtures unless you have a really great reason not to.
## Renaming Fixtures
The name of a fixture, listed in the parameter list of tests and other fixtures using it, is usually the same as the function name of the fixture. However, pytest allows you to rename fixtures with a **name** parameter to [``@pytest.fixture()``](./test_rename_fixture.py):
```python
import pytest


@pytest.fixture(name="ultimate_answer")
def ultimate_answer_fixture():
    return 42


def test_everything(ultimate_answer):
    assert ultimate_answer == 42
```
I’ve run across a few examples where renaming is desirable. As in this example, some people like to name their fixtures with a`` _fixture`` suffix or ``fixture_`` prefix or similar.

One instance where renaming is useful is when [the most obvious fixture name](./test_rename_2.py) already exists as an existing variable or function name:
```python
import pytest
from somewhere import app


@pytest.fixture(scope="session", name="app")
def _app():
    """The app object"""
    yield app()


def test_that_uses_app(app):
    assert app.some_property == "something"
```
I usually only use fixture renaming with a fixture that lives in the same module as the tests using it, as renaming a fixture can make it harder to find where it’s defined. However, remember that there is always ``--fixtures``, which can help you find where a fixture lives.
## Review
In this chapter, we covered a lot about fixtures:
* Fixtures are ``@pytest.fixture()`` decorated functions.
* Test functions or other fixtures depend on a fixture by putting its name in their parameter list.
* Fixtures can return data using ``return`` or ``yield``.
* Code before the ``yield`` is the setup code. Code after the ``yield`` is the teardown code.
* Fixtures can be set to function, class, module, package, or session scope. The default is function scope. You can even define the scope dynamically.
* Multiple test functions can use the same fixture.
* Multiple test modules can use the same fixture if it’s in a ``conftest.py`` file.
* Multiple fixtures at different scope can speed up test suites while maintaining test isolation.
* Tests and fixtures can use multiple fixtures.
* Autouse fixtures don’t have to be named by the test function.
* You can have the name of a fixture be different than the fixture function name.


We also covered a few new command-line flags:
* ``pytest --setup-show`` is used to see the order of execution.
* ``pytest --fixtures`` is used to list available fixtures and where the fixture is located.
* ``-s`` and ``--capture=no`` allow print statements to be seen even in passing tests.
## Exercises
Fixtures are often one of the trickier parts of pytest for people to get used to. Going through the following exercises will
* help solidify your understanding of how fixtures work,
* llow you to use different fixture scopes, and
* internalize the run sequence with the visual output of `--setup-show`.
1. Create a test file called `test_fixtures.py`.
2. Write a few data fixtures—functions with the `@pytest.fixture()` decorator—that return some data (perhaps a list, dictionary, or tuple).
3. For each fixture, write at least one test function that uses it.
4. Write two tests that use the same fixture.
5. Run `pytest --setup-show test_fixtures.py`. Are all the fixtures run before every test?
6. Add `scope=’module’` to the fixture from Exercise 4.
7. Re-run `pytest --setup-show test_fixtures.py`. What changed?
8. For the fixture from Exercise 6, change `return <data>` to `yield <data>`.
9. Add print statements before and after the yield.
10. Run `pytest -s -v test_fixtures.py`. Does the output make sense?
11. Run `pytest --fixtures`. Can you see your fixtures listed?
12. Add a docstring to one of your fixtures, if you didn’t include them already. Re-run `pytest --fixtures` to see the description show up.