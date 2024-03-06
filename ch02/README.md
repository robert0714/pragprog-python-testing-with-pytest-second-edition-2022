# Writing Test Functions
We’re going to write tests for a simple task-tracking command-line application called **Cards**. We’ll look at how to use **assert** in tests, how tests handle unexpected exceptions, and how to test for expected exceptions.
## Installing the Sample Application
The test code we write needs to be able to run the application code. The “application code” is the code we are validating, and it has many names. You may hear it referred to as production code, the application, code under test (CUT), system under test (SUT), device under test (DUT), and so on. For this book, we’ll use the term “application code” if it’s necessary to distinguish the code from the test code.

The “test code” is the code we are writing in order to test the application code. Ironically, “test code” is fairly unambiguous and doesn’t have many names other than “test code.”

In our case, the Cards project is the application code. It is an installable Python package, and we need to install it in order to test it. Installing it will also allow us to play with the Cards project on the command line. If the code you are testing is not a Python package that can be installed, you’ll have to use other ways to get your test to see your code. (Some alternatives are discussed in Chapter 12, ​Testing Scripts and Applications​.)

The Cards project is at ``/path/to/code/cards_project``, and the tests for this chapter are at ``/path/to/code/ch02``.

You can use the same virtual environment you used in the previous chapter, create new environments for each chapter, or create one for the whole book. Let’s create one at the /path/to/code/ level and use that until we need to use something different:
```bash
​$ ​​cd​​ ​​/path/to/code​
​$ ​​python​​ ​​-m​​ ​​venv​​ ​​venv​
​$ ​​source​​ ​​venv/bin/activate​
```
       
And now, with the virtual environment activated, install the local **cards_proj** application. The ``./`` in front of ``./cards_proj/`` tells **pip** to look in the local directory, instead of trying to install from PyPI.
```bash
       (venv) $ pip install ./cards_proj/
       Processing ./cards_proj
       ​...​
       Successfully built cards
       Installing collected packages: cards
       Successfully installed cards
```
we can see the installed path:
  * anaconda: ``${ANACONDA_ENV}/${ENV}/Scripts/cards``
  * basic python : ``/home/${USER}/.local/bin/cards``
  * virtual environment (​venv)​: ``​venv/bin/cards``

While we’re at it, let’s make sure pytest is installed, too:
```bash
       (venv) $ pip install pytest
```
For each new virtual environment, we have to install everything we need, including pytest.

For the rest of the book, even though I will be working within a virtual environment, I’ll only show ``$`` as a command prompt instead of ``(venv) $`` merely to save horizontal space and visual noise.

Let’s run ``cards`` and play with it a bit:
```bash
       $ ​​cards​​ ​​add​​ ​​do​​ ​​something​​ ​​--owner​​ ​​Brian​
       ​$ ​​cards​​ ​​add​​ ​​do​​ ​​something​​ ​​else​
       ​$ ​​cards​
         ID   state   owner   summary
        ────────────────────────────────────────
         1    todo    Brian   do something
         2    todo            do something else
       ​$ ​​cards​​ ​​update​​ ​​2​​ ​​--owner​​ ​​Brian​
       ​$ ​​cards​
         ID   state   owner   summary
        ────────────────────────────────────────
         1    todo    Brian   do something
         2    todo    Brian   do something else
       ​$ ​​cards​​ ​​start​​ ​​1​
       ​$ ​​cards​​ ​​finish​​ ​​1​
       ​$ ​​cards​​ ​​start​​ ​​2​
       ​$ ​​cards​
         ID   state     owner   summary
        ──────────────────────────────────────────
         1    done      Brian   do something
         2    in prog   Brian   do something else
       ​$ ​​cards​​ ​​delete​​ ​​1​
       ​$ ​​cards​
         ID   state     owner   summary
        ──────────────────────────────────────────
         2    in prog   Brian   do something else
```

These examples show that a todo item, or “card,” can be manipulated with the actions ``add, update, start, finish``, and ``delete``, and that running ``cards`` with no action will list the cards.

Nice. Now we’re ready to write some tests.

## Writing Knowledge-Building Tests
The Cards source code is split into three layers: CLI, API, and DB. The CLI handles the interaction with the user. The CLI calls the **API**, which handles most of the **logic** of the application. The API calls into the DB layer (the database), for saving and retrieving application data. We’ll look at the structure of Cards more in ​Considering Software Architecture​.

There’s a data structure used to pass information between the ClI and the API, a data class called **Card**:  (  cards_proj/src/cards/api.py)
```python
@dataclass
​class​ Card:
    summary: str = None
    owner: str = None
    state: str = ​"todo"​
    id: int = field(default=None, compare=False)

    @classmethod
    ​def​ ​from_dict​(cls, d):
        ​return​ Card(**d)
​def​ ​to_dict​(self):
    ​return​ asdict(self)
```
**Data classes** were added to Python in version 3.7, but they may still be new to some. The **Card** structure has three string fields: ``summary, owner, and state``, and one integer field: ``id``. The ``summary, owner``, and ``id`` fields default to ``None``. The ``state`` field defaults to "``todo``". The `id` field is also using the ``field`` method to utilize ``compare=False``, which is supposed to tell the code that when comparing two `Card` objects for equality, to not use the ``id`` field. We will definitely test that, as well as the other aspects. A couple of other methods were added for convenience and clarity: ``from_dict`` and ``to_dict``, since ``Card(**d)`` or ``dataclasses.asdict()`` aren’t very easy to read.

When faced with a new data structure, it’s often helpful to write some quick tests so that you can understand how the data structure works. So, let’s start with some tests that verify our understanding of how this thing is supposed to work:
```python
​from​ ​cards​ ​import​ Card


​def​ ​test_field_access​():
    c = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    ​assert​ c.summary == ​"something"​
    ​assert​ c.owner == ​"brian"​
    ​assert​ c.state == ​"todo"​
    ​assert​ c.id == 123


​def​ ​test_defaults​():
    c = Card()
    ​assert​ c.summary ​is​ None

​from​ ​cards​ ​import​ Card


​def​ ​test_field_access​():
    c = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    ​assert​ c.summary == ​"something"​
    ​assert​ c.owner == ​"brian"​
    ​assert​ c.state == ​"todo"​
    ​assert​ c.id == 123


​def​ ​test_defaults​():
    c = Card()
    ​assert​ c.summary ​is​ None
    ​assert​ c.owner ​is​ None
    ​assert​ c.state == ​"todo"​
    ​assert​ c.id ​is​ None


​def​ ​test_equality​():
    c1 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    c2 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    ​assert​ c1 == c2


​def​ ​test_equality_with_diff_ids​():
    c1 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    c2 = Card(​"something"​, ​"brian"​, ​"todo"​, 4567)
    ​assert​ c1 == c2
​def​ ​test_inequality​():
    c1 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    c2 = Card(​"completely different"​, ​"okken"​, ​"done"​, 123)
    ​assert​ c1 != c2


​def​ ​test_from_dict​():
    c1 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    c2_dict = {
        ​"summary"​: ​"something"​,
        ​"owner"​: ​"brian"​,
        ​"state"​: ​"todo"​,
        ​"id"​: 123,
    }
    c2 = Card.from_dict(c2_dict)
    ​assert​ c1 == c2


​def​ ​test_to_dict​():
    c1 = Card(​"something"​, ​"brian"​, ​"todo"​, 123)
    c2 = c1.to_dict()
    c2_expected = {
        ​"summary"​: ​"something"​,
        ​"owner"​: ​"brian"​,
        ​"state"​: ​"todo"​,
        ​"id"​: 123,
    }
    ​assert​ c2 == c2_expected
```

Do a quick test run:
```bash
$ pytest test_card.py
```

We could have started with one test. However, I want to demonstrate just how quickly and concisely we can write a bunch of tests. These tests are intended to demonstrate how to use a data structure. They aren’t exhaustive tests; they are not looking for corner cases, or failure cases, or looking for ways to make the data structure blow up. I haven’t tried passing in gibberish or negative numbers as IDs or huge strings. That’s not the point of this set of tests.

The point of these tests is to check my understanding of how the structure works, and possibly to document that knowledge for someone else or even for a future me. This use of checking my own understanding, and really of using tests as little playgrounds to play with the application code, is super powerful, and I think more people would enjoy testing more if they start with this mindset.

Note also that all of these tests use plain old ``assert`` statements. Let’s take a look at them next.
## Using assert Statements
When you write test functions, the normal Python ``assert`` statement is your primary tool to communicate test failure. The simplicity of this within pytest is brilliant. It’s what drives a lot of developers to use pytest over other frameworks.

If you’ve used any other testing framework, you’ve probably seen various ``assert`` helper functions. For example, following is a list of a few of the ``assert`` forms and ``assert`` helper functions from unittest:

| pytest                | unittest               |
|-----------------------|------------------------|
| assert something      | assertTrue(something)  |
| assert not something  | assertFalse(something) |
| assert a == b         | assertEqual(a, b)      |
| assert a != b         | assertNotEqual(a, b)   |
| assert a is None      | assertIsNone(a)        |
| assert a is not None  | assertIsNotNone(a)     |
| assert a <= b         | assertLessEqual(a, b)  |

With pytest, you can use ``assert <expression>`` with any expression. If the expression would evaluate to ``False`` if converted to a ``bool``, the test would fail.

pytest includes a feature called “assert rewriting” that intercepts ``assert`` calls and replaces them with something that can tell you more about why your assertions failed. Let’s see how helpful this rewriting is by looking at an assertion failure:
```python
​def​ ​test_equality_fail​():
    c1 = Card(​"sit there"​, ​"brian"​)
    c2 = Card(​"do something"​, ​"okken"​)
    assert​ c1 == c2
```

This test will fail, but what’s interesting is the traceback information:
```bash
​$ ​​pytest​​ ​​test_card_fail.py
​$ ​​pytest​​ ​​-vv​​ ​​test_card_fail.py
```
Well, I think that’s pretty darned cool. pytest listed specifically which attributes matched and which did not, and highlighted the exact mismatches.

The previous example only used equality ``assert``; many more varieties of assert statements with awesome trace debug information are found on the pytest.org website.

Just for reference, we can see what Python gives us by default for assert failures. We can run the test, not from pytest, but directly from Python by adding a ``if__name__ == ’__main__’`` block at the end of the file and calling ``test_equality_fail()``, like this:
```python
if​ __name__ == ​"__main__"​:
    test_equality_fail()
```
Using ``if__name__ == ’__main__’`` is a quick way to run some code from a file but not allow the code to be run if it is imported. When a module is imported, Python will fill in ``__name__`` with the name of the module, which is the name of the file without the .py. However, if you run the file with ``python file.py``, ``__name__`` will be filled in by Python with the string ``"__main__"``.

Running the test with straight Python, we get this:
```python
 	$ python test_card_fail.py
​ 	Traceback (most recent call last):
​ 	  File "/path/to/code/ch02/test_card_fail.py", line 12, in <module>
​ 	    test_equality_fail()
​ 	  File "/path/to/code/ch02/test_card_fail.py", line 7, in test_equality_fail
​ 	    assert c1 == c2
​ 	AssertionError
```
That doesn’t tell us much. The pytest version gives us way more information about why our assertions failed.

Assertion failures are the primary way test code results in a failed test. However, it’s not the only way.

## Failing with pytest.fail() and Exceptions
A test will fail if there is any uncaught exception. This can happen if
* an **assert** statement fails, which will raise an **AssertionError** exception,
* the test code calls ``pytest.fail()``, which will raise an exception, or
* any other exception is raised.

While any exception can fail a test, I prefer to use **assert**. In rare cases where **assert** is not suitable, use ``pytest.fail()``.

Here’s what the output looks like:
```bash
$ pytest  test_alt_fail.py
=========================================================================================================== test session starts ============================================================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 1 item

test_alt_fail.py F                                                                                                                                                                                                                    [100%]

================================================================================================================= FAILURES =================================================================================================================
______________________________________________________________________________________________________________ test_with_fail ______________________________________________________________________________________________________________

    def test_with_fail():
        c1 = Card("sit there", "brian")
        c2 = Card("do something", "okken")
        if c1 != c2:
>           pytest.fail("they don't match")
E           Failed: they don't match

test_alt_fail.py:9: Failed
========================================================================================================= short test summary info ==========================================================================================================
FAILED test_alt_fail.py::test_with_fail - Failed: they don't match
============================================================================================================ 1 failed in 0.17s =============================================================================================================
```
When calling ``pytest.fail()`` or raising an exception directly, we don’t get the wonderful assert rewriting provided by pytest. However, there are reasonable times to use ``pytest.fail()``, such as in an assertion helper.
## Writing Assertion Helper Functions
An assertion helper is a function that is used to wrap up a complicated assertion check. As an example, the Cards data class is set up such that two cards with different IDs will still report equality. If we wanted to have a stricter check, we could write a helper function called **assert_identical** like this:
```python
from cards import Card
import pytest


def assert_identical(c1: Card, c2: Card):
    __tracebackhide__ = True
    assert c1 == c2
    if c1.id != c2.id:
        pytest.fail(f"id's don't match. {c1.id} != {c2.id}")


def test_identical():
    c1 = Card("foo", id=123)
    c2 = Card("foo", id=123)
    assert_identical(c1, c2)


def test_identical_fail():
    c1 = Card("foo", id=123)
    c2 = Card("foo", id=456)
    assert_identical(c1, c2)
```
The ``assert_identical`` function sets ``__tracebackhide__ = True``. This is optional. The effect will be that failing tests will not include this function in the traceback. The normal ``assert c1 == c2`` is then used to check everything except the ID for equality.

Finally, the IDs are checked, and if they are not equal, ``pytest.fail()`` is used to fail the test with a hopefully helpful message.

Let’s see what that looks like when run:

```bash
$ pytest test_helper.py
=========================================================================================================== test session starts ============================================================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 2 items

test_helper.py .F                                                                                                                                                                                                                     [100%]

================================================================================================================= FAILURES =================================================================================================================
___________________________________________________________________________________________________________ test_identical_fail ____________________________________________________________________________________________________________

    def test_identical_fail():
        c1 = Card("foo", id=123)
        c2 = Card("foo", id=456)
>       assert_identical(c1, c2)
E       Failed: id's don't match. 123 != 456

test_helper.py:21: Failed
========================================================================================================= short test summary info ==========================================================================================================
FAILED test_helper.py::test_identical_fail - Failed: id's don't match. 123 != 456
======================================================================================================= 1 failed, 1 passed in 0.22s ========================================================================================================
```

If we had not put in the ``__tracebackhide__ = True``, the ``assert_identical`` code would have been included in the traceback, which in this case, wouldn’t have added any clarity. I could have also used ``assert c1.id == c2.id, "id’s don’t match."`` to much the same effect, but I wanted to show an example of using ``pytest.fail()``.

Note that assert rewriting is only applied to conftest.py files and test files. See [the pytest documentation](https://docs.pytest.org/en/latest/how-to/assert.html#assertion-introspection-details) for more details.

## Testing for Expected Exceptions
We’ve looked at how any exception can cause a test to fail. But what if a bit of code you are testing is supposed to raise an exception? How do you test for that?

You use ``pytest.raises()`` to test for expected exceptions.

As an example, the ``cards`` API has a ``CardsDB`` class that requires a path argument. What happens if we don’t pass in a path? Let’s try it( test_experiment.py)::
```python
import cards

def test_no_path_fail():
    cards.CardsDB()
```
Let’s see what that looks like when run:
```bash
$ pytest --tb=short test_exceptions.py
=========================== test session starts ============================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 3 items

test_exceptions.py ...                                                [100%]

============================ 3 passed in 0.11s =============================
```
Here I used the ``--tb=short`` shorter traceback format because we don’t need to see the full traceback to find out which exception is raised.

The ``TypeError`` exception seems reasonable, since the error occurs when trying to initialize the custom ``CardsDB`` type. We can write a test to make sure this exception is thrown, like this ( test_exceptions.py):
```python
import pytest
import cards


def test_no_path_raises():
    with pytest.raises(TypeError):
        cards.CardsDB()


def test_raises_with_info():
    match_regex = "missing 1 .* positional argument"
    with pytest.raises(TypeError, match=match_regex):
        cards.CardsDB()


def test_raises_with_info_alt():
    with pytest.raises(TypeError) as exc_info:
        cards.CardsDB()
    expected = "missing 1 required positional argument"
    assert expected in str(exc_info.value)
```
The ``with pytest.raises(TypeError)``: statement says that whatever is in the next block of code should raise a ``TypeError`` exception. If no exception is raised, the test fails. If the test raises a different exception, it fails.

We just checked for the type of exception in ``test_no_path_raises()``. We can also check to make sure the message is correct, or any other aspect of the exception, like additional parameters ( test_exceptions.py):
```python
def test_raises_with_info():
    match_regex = "missing 1 .* positional argument"
    with pytest.raises(TypeError, match=match_regex):
        cards.CardsDB()


def test_raises_with_info_alt():
    with pytest.raises(TypeError) as exc_info:
        cards.CardsDB()
    expected = "missing 1 required positional argument"
    assert expected in str(exc_info.value)
```
The ``match`` parameter takes a regular expression and matches it with the exception message. You can also use ``as exc_info`` or any other variable name to interrogate extra parameters to the exception if it’s a custom exception. The ``exc_info`` object will be of type ``ExceptionInfo``. See [the pytest documentation](https://docs.pytest.org/en/latest/reference/reference.html#exceptioninfo) for full ``ExceptionInfo`` reference.

## Structuring Test Functions
I recommend making sure you keep assertions at the end of test functions. This is such a common recommendation that it has at least two names: 
  * Arrange-Act-Assert
  * Given-When-Then.

Bill Wake originally named [the Arrange-Act-Assert pattern in 2001](https://xp123.com/articles/3a-arrange-act-assert). Kent Beck later popularized the practice as part of test-driven development ([TDD](https://en.wikipedia.org/wiki/Test-driven_development)). Behavior-driven development (BDD) uses the terms Given-When-Then, a pattern from Ivan Moore, popularized by [Dan North](https://dannorth.net/introducing-bdd). Regardless of the names of the steps, the goal is the same: separate a test into stages.

There are many benefits of separating into stages. The separation clearly separates the “getting ready to do something,” the “doing something,” and the “checking to see if it worked” parts of the test. That allows the test developer to focus attention on each part, and be clear about what is really being tested.

A common anti-pattern is to have more a ``“Arrange-Assert-Act-Assert-Act-Assert…”`` pattern where lots of actions, followed by state or behavior checks, validate a workflow. This seems reasonable until the test fails. Any of the actions could have caused the failure, so the test is not focusing on testing one behavior. Or it might have been the setup in “Arrange” that caused the failure. This interleaved ``assert`` pattern creates tests that are hard to debug and maintain because later developers have no idea what the original intent of the test was. Sticking to Given-When-Then or Arrange-Act-Assert keeps the test focused and makes the test more maintainable.

The three-stage structure is the structure I try to stick to with my own test functions and the tests in this book.

Let’s apply this structure to one of our first tests as an [example](./test_structure.py):
```python
def test_to_dict():
    # GIVEN a Card object with known contents
    c1 = Card("something", "brian", "todo", 123)

    # WHEN we call to_dict() on the object
    c2 = c1.to_dict()

    # THEN the result will be a dictionary with known content
    c2_expected = {
        "summary": "something",
        "owner": "brian",
        "state": "todo",
        "id": 123,
    }
    assert c2 == c2_expected
```
* ``Given/Arrange`` — A starting state. This is where you set up data or the environment to get ready for the action.
* ``When/Act`` — Some action is performed. This is the focus of the test—the behavior we are trying to make sure is working right.
* ``Then/Assert`` — Some expected result or end state should happen. At the end of the test, we make sure the action resulted in the expected behavior.

I tend to think about tests more naturally using the Given-When-Then terms. Some people find it more natural to use Arrange-Act-Assert. Both ideas work fine. The structure helps to keep test functions organized and focused on testing one behavior. The structure also helps you to think of other test cases. Focusing on one starting state helps you think of other states that might be relevant to test with the same action. Likewise, focusing on one ideal outcome helps you think of other possible outcomes, like failure states or error conditions, that should also be tested with other test cases.

## Grouping Tests with Classes
So far we’ve written test functions within test modules within a file system directory. That structuring of test code actually works quite well and is sufficient for many projects. However, pytest also allows us to group tests with classes.

Let’s take a few of the test functions related to ``Card`` equality and group them into [a class](./test_classes.py?plain=1#L20-L33):
```python
class TestEquality:
    def test_equality(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("something", "brian", "todo", 123)
        assert c1 == c2
    def test_equality_with_diff_ids(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("something", "brian", "todo", 4567)
        assert c1 == c2

    def test_inequality(self):
        c1 = Card("something", "brian", "todo", 123)
        c2 = Card("completely different", "okken", "done", 123)
        assert c1 != c2
```
The code looks pretty much the same as it did before, with the exception of some extra white space and each method has to have an initial **self** argument.

We can now run all of these together by specifying the class:
```bash
$ pytest -v test_classes.py::TestEquality

=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 3 items

test_classes.py::TestEquality::test_equality PASSED                                                                                                   [ 33%]
test_classes.py::TestEquality::test_equality_with_diff_ids PASSED                                                                                     [ 66%]
test_classes.py::TestEquality::test_inequality PASSED                                                                                                 [100%]

==================================================================== 3 passed in 0.13s =====================================================================
```
We can still get at a single method:
```bash
 pytest -v .\test_classes.py::TestEquality::test_equality
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 1 item

test_classes.py::TestEquality::test_equality PASSED                                                                                                   [100%]

==================================================================== 1 passed in 0.10s =====================================================================
```
If you are familiar with object-oriented programming (OOP) and class inheritance with Python, you can utilize test class hierarchies for inherited helper methods. If you are not familiar with OOP and such, don’t worry about it. In this book, and in almost all of my own use of test classes, I use them solely for the purpose of grouping tests to easily run them together. I recommend that in production test code, you also use test classes sparingly and primarily for grouping. Getting fancy with test class inheritance will certainly confuse someone, possibly yourself, in the future.
## Running a Subset of Tests
In the previous section, we used test classes to be able to run a subset of tests. Running just a small batch of tests is handy while debugging or if you want to limit the tests to a specific section of the code base you are working on at the time.

pytest allows you to run a subset of tests in several ways:

| Subset                         | Syntax                                             |
|--------------------------------|----------------------------------------------------|
| Single test method             | pytest path/test_module.py::TestClass::test_method |
| All tests in a class           | pytest path/test_module.py::TestClass              |
| Single test function           | pytest path/test_module.py::test_function          |
| All tests in a module          | pytest path/test_module.py                         |
| All tests in a directory       | pytest path                                        |
| Tests matching a name pattern  | pytest -k pattern                                  |
| Tests by marker                | Covered in Chapter 6, [​Markers](./ch06/README.md)​.    |

We’ve used everything but pattern and marker subsets so far. But let’s run through examples anyway.

We’ll start from the top-level code directory so that we can use **ch02** to show the path in the command-line examples:
```bash
​$ cd /path/to/code
```
Running a single test method, test class, or module:
```bash
​ 	$ pytest ch02/test_classes.py::TestEquality::test_equality
​ 	$ pytest ch02/test_classes.py::TestEquality
​ 	$ pytest ch02/test_classes.py
```
Running a single test function or module:
```bash
​ 	$ pytest ch02/test_card.py::test_defaults
​ 	$ pytest ch02/test_card.py
```
Running the whole directory:
```bash
​ 	$ pytest ch02
```
We’ll cover markers in Chapter 6, [​Markers](./ch06/README.md), but let’s talk about **-k** here.
The ``-k`` argument takes an expression, and tells pytest to run tests that contain a substring that matches the expression. The substring can be part of the test name or the test class name. Let’s take a look at using ``-k`` in action.

We know we can run the tests in the TestEquality class with:
```bash
​ 	$ pytest ch02/test_classes.py::TestEquality
```
We can also use -k and just specify the test class name:
```bash
​ 	$ cd /path/to/code/ch02
​ 	$ pytest -v -k TestEquality
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 23 items / 20 deselected / 3 selected

test_classes.py::TestEquality::test_equality PASSED                                                                                                   [ 33%]
test_classes.py::TestEquality::test_equality_with_diff_ids PASSED                                                                                     [ 66%]
test_classes.py::TestEquality::test_inequality PASSED                                                                                                 [100%]

============================================================= 3 passed, 20 deselected in 0.14s =============================================================
```
or even just part of the name:
```bash
​ 	$ cd /path/to/code/ch02
​ 	$ pytest -v -k TestEqu
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 23 items / 20 deselected / 3 selected

test_classes.py::TestEquality::test_equality PASSED                                                                                                   [ 33%]
test_classes.py::TestEquality::test_equality_with_diff_ids PASSED                                                                                     [ 66%]
test_classes.py::TestEquality::test_inequality PASSED                                                                                                 [100%]

============================================================= 3 passed, 20 deselected in 0.14s =============================================================
```

Let’s run all the tests with “equality” in their name:
```bash
​ 	$ cd /path/to/code/ch02
​ 	$ pytest -v --tb=no -k equality
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 23 items / 16 deselected / 7 selected

test_card.py::test_equality PASSED                                                                                                                    [ 14%]
test_card.py::test_equality_with_diff_ids PASSED                                                                                                      [ 28%]
test_card.py::test_inequality PASSED                                                                                                                  [ 42%]
test_card_fail.py::test_equality_fail FAILED                                                                                                          [ 57%]
test_classes.py::TestEquality::test_equality PASSED                                                                                                   [ 71%]
test_classes.py::TestEquality::test_equality_with_diff_ids PASSED                                                                                     [ 85%]
test_classes.py::TestEquality::test_inequality PASSED                                                                                                 [100%]

================================================================= short test summary info ==================================================================
FAILED test_card_fail.py::test_equality_fail - AssertionError: assert Card(summary=...odo', id=None) == Card(summary=...odo', id=None)
======================================================== 1 failed, 6 passed, 16 deselected in 0.17s ========================================================
```
Yikes. One of those is our fail example. We can eliminate that by expanding the expression:
```bash
​ 	$ cd /path/to/code/ch02
​ 	$ pytest -v --tb=no -k "equality and not equality_fail"
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 23 items / 17 deselected / 6 selected

test_card.py::test_equality PASSED                                                                                                                    [ 16%]
test_card.py::test_equality_with_diff_ids PASSED                                                                                                      [ 33%]
test_card.py::test_inequality PASSED                                                                                                                  [ 50%]
test_classes.py::TestEquality::test_equality PASSED                                                                                                   [ 66%]
test_classes.py::TestEquality::test_equality_with_diff_ids PASSED                                                                                     [ 83%]
test_classes.py::TestEquality::test_inequality PASSED                                                                                                 [100%]

============================================================= 6 passed, 17 deselected in 0.11s =============================================================
```
The keywords and, not, or, and parentheses are allowed to create complex expressions. Here’s a test run of all tests with “dict” or “ids” in the name, but not ones in the “TestEquality” class:
```bash
​ 	$ cd /path/to/code/ch02
​ 	$ pytest -v --tb=no -k "(dict or ids) and not TestEquality"
=================================================================== test session starts ====================================================================
platform win32 -- Python 3.8.18, pytest-8.0.2, pluggy-1.4.0 -- E:\anaconda_envs_dirs\test\python.exe
cachedir: .pytest_cache
rootdir: E:\python_workspaces\pragprog-python-testing-with-pytest-second-edition-2022
configfile: pytest.ini
collected 23 items / 17 deselected / 6 selected

test_card.py::test_equality_with_diff_ids PASSED                                                                                                      [ 16%]
test_card.py::test_from_dict PASSED                                                                                                                   [ 33%]
test_card.py::test_to_dict PASSED                                                                                                                     [ 50%]
test_classes.py::test_from_dict PASSED                                                                                                                [ 66%]
test_classes.py::test_to_dict PASSED                                                                                                                  [ 83%]
test_structure.py::test_to_dict PASSED                                                                                                                [100%]

============================================================= 6 passed, 17 deselected in 0.13s =============================================================
```
The keyword flag, ``-k``, along with and, not, and or, add quite a bit of flexibility to selecting exactly the tests you want to run. This really proves quite helpful when debugging failures or developing new tests.