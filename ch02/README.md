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
​ 	  File "/path/to/code/ch2/test_card_fail.py", line 12, in <module>
​ 	    test_equality_fail()
​ 	  File "/path/to/code/ch2/test_card_fail.py", line 7, in test_equality_fail
​ 	    assert c1 == c2
​ 	AssertionError
```
That doesn’t tell us much. The pytest version gives us way more information about why our assertions failed.

Assertion failures are the primary way test code results in a failed test. However, it’s not the only way.