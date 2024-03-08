# Chapter 15 Building Plugins
In the last chapter, we talked about the wealth of plugins available. As you progress with using pytest, you will undoubtedly create fixtures and new command-line flags and all sorts of new cool things that you will want to use on more than one project. You may even want to share the modifications with others and publish your changes. This chapter is exactly about how to share pytest modifications by building your own plugins.

## Starting with a Cool Idea
Maybe “cool idea” is too strong a phrase. An idea doesn’t have to be really that cool to deserve being made into a plugin. It just needs to be helpful. You may have a fixture or command-line flag that’s useful on one project, and you want to use on other projects. That’s good enough for plugin-hood.

As an example, we’ll grab an idea from the pytest documentation about slow tests. The [pytest documentation](https://docs.pytest.org/en/7.0.x/example/simple.html#control-skipping-of-tests-according-to-command-line-option) includes an examples page with a description of how to skip tests that are marked with ``@pytest.mark.slow`` automatically.

Here’s the idea (the documentation actually uses --runslow, but we’ll use --slow because it’s shorter and seems like a better flag to me):
* Mark tests with ``@pytest.mark.slow`` that are so slow you don’t want to always run them.
* When pytest collects tests to run, intercept that process by adding an extra mark—``@pytest.mark.skip(reason="need --runslow option to run")``—on all tests marked with ``@pytest.mark.slow``. That way, these tests will be skipped by default.
* Add the ``--slow`` flag so that users can override this behavior and actually run the slow tests. Under normal circumstances, whenever you run pytest, the tests marked slow will be skipped. However, the ``--slow`` flag will run all the tests, including the slow tests.
* To run just the slow tests, you can still select the marker with ``-m slow``, but you have to combine it with ``--slow``, so ``-m slow --slow`` will run only the slow tests.

This actually seems like a very useful idea. We’ll develop this idea into a full plugin in this chapter. Along the way, you’ll learn how to test plugins, how to package them, and how to publish them on PyPI. You’ll also learn about hook functions, as we’ll use them to implement this plugin.

We can already use markers to select or exclude specific tests. With`` --slow``, we’re just trying to change the default to exclude tests marked with “slow”: 
  
| Behavior     | Without plugin       | With plugin            |
|--------------|----------------------|------------------------|
| Exclude slow | pytest -m "not slow" | pytest                 |
| Include slow | pytest               | pytest --slow          |
| Only slow    | pytest -m slow       | pytest -m slow --slow  |


I set up a short test file and configuration file as a playground for the original behavior.

The test file looks like this:

[ch15/just_markers/test_slow.py](./just_markers/test_slow.py)
```python
import pytest


def test_normal():
    pass


@pytest.mark.slow
def test_slow():
    pass
```
​
And here’s the configuration file to declare “slow”:

[ch15/just_markers/pytest.ini](./just_markers/pytest.ini)
```ini
​ 	​[pytest]​
​ 	markers = ​slow: mark test as slow to run​
```
The behavior we’re trying to make easier, avoiding slow tests, looks like this:
```bash
​ 	​$ ​​cd​​ ​​path/to/code/ch15/just_markers​
​ 	​$ ​​pytest​​ ​​-v​​ ​​-m​​ ​​"not slow"​
​ 	========================= test session starts ==========================
​ 	collected 2 items / 1 deselected / 1 selected
​ 	
​ 	test_slow.py::test_normal PASSED                                 [100%]
​ 	
​ 	=================== 1 passed, 1 deselected in 0.01s ====================
```
Great. Now that we know what we’re shooting for, let’s begin.
## Building a Local conftest Plugin
We’ll start by making changes in a ``conftest.py`` file and testing our changes locally before moving the code to a plugin.

To modify how pytest works, we need to utilize pytest hook functions. [Hook functions](https://docs.pytest.org/en/6.2.x/writing_plugins.html#writinghooks) are function entry points that pytest provides to allow plugin developers to intercept pytest behavior at certain points and make changes. The pytest documentation lists a lot of [hook functions](https://docs.pytest.org/en/latest/reference/reference.html#hook-reference). We’ll use three in this chapter:
* ``pytest_configure()``—Allows plugins and conftest files to perform initial configuration. We’ll use this hook function to pre-declare the ``slow`` marker so users don’t have to add ``slow`` to their config files.
* ``pytest_addoption()``—Used to register options and settings. We’ll add the ``--slow`` flag with this hook.
* ``pytest_collection_modifyitems()``—Called after test collection has been performed and can be used to filter or re-order the test items. We need this to find the ``slow`` tests, so we can mark them for skipping.

Let’s start with ``pytest_configure()`` and declare the ``slow`` marker:

[ch15/local/conftest.py](./local/conftest.py)
```python
​ 	​import​ ​pytest​
​ 	
​ 	
​ 	​def​ ​pytest_configure​(config):
​ 	    config.addinivalue_line(​"markers"​, ​"slow: mark test as slow to run"​)
```
Now we need to use ``pytest_addoption()`` to add the ``--slow`` flag:

[ch15/local/conftest.py](./local/conftest.py)
```python
​ 	​def​ ​pytest_addoption​(parser):
​ 	    parser.addoption(
​ 	        ​"--slow"​, action=​"store_true"​, help=​"include tests marked slow"​
​ 	    )
```
The call to ``parser.addoption()`` creates the flag and the configuration setting. The action="store_true" parameter tells pytest to store a ``true`` in the ``slow`` configuration setting when the ``--slow`` flag is passed in, and false otherwise. The ``help="include tests marked slow"`` creates a line in the ``help`` output to describe the flag:
```bash
​ 	​$ ​​cd​​ ​​path/to/code/ch15/local​
​ 	​$ ​​pytest​​ ​​--help​
​ 	​...​
​ 	custom options:
​ 	  --slow                include tests marked slow
​ 	​...​
```
Now for the fun part—actually modifying the tests that get run:

[ch15/local/conftest.py](./local/conftest.py)
```python
​ 	​def​ ​pytest_collection_modifyitems​(config, items):
​ 	    ​if​ ​not​ config.getoption(​"--slow"​):
​ 	        skip_slow = pytest.mark.skip(reason=​"need --slow option to run"​)
​ 	        ​for​ item ​in​ items:
​ 	            ​if​ item.get_closest_marker(​"slow"​):
​ 	                item.add_marker(skip_slow)
```
This code uses the suggestion in the pytest documentation to add a skip marker to any test that already includes the ``slow`` marker. We use ``config.getoption("--slow")`` to get the slow setting. We can also use ``config.getoption("slow")``. Both work the same. But I find that including the dashes is more readable.

The ``items`` value passed to ``pytest_collection_modifyitems()`` will be the list of tests pytest intends to run. Specifically, it’s a list of ``Node`` objects. Now we’re really getting into the guts of pytest implementation.

The [Node interface](https://docs.pytest.org/en/latest/reference/reference.html#node) includes two methods we care about: ``get_closest_marker``() and ``add_marker().get_closest_marker("slow")`` will return a marker object if there is a “slow” marker on the test. If there is no “slow” marker on the test, the ``get_closest_marker("slow")`` will return None. Here we’re using the return value as a boolean True or False to see if “slow” is a marker on the test. If it is, we add the skip marker. If the method returns an object, it will act like a True value in an if clause. A ``None`` value evaluates to False in an if clause. Let’s try it out:
```bash
​ 	​$ ​​pytest​​ ​​-v​
​ 	========================= test session starts ==========================
​ 	collected 2 items
​ 	
​ 	test_slow.py::test_normal PASSED                                 [ 50%]
​ 	test_slow.py::test_slow SKIPPED (need --slow option to run)      [100%]
​ 	
​ 	===================== 1 passed, 1 skipped in 0.01s =====================
```
By default, we avoid our slow test by skipping it. It’s not quite the same as deselecting it. However, it is nice that the reason is listed in the verbose output.

We can also include the test with ``--slow``:
```bash
​ 	​$ ​​pytest​​ ​​-v​​ ​​--slow​
​ 	========================= test session starts ==========================
​ 	collected 2 items
​ 	
​ 	test_slow.py::test_normal PASSED                                 [ 50%]
​ 	test_slow.py::test_slow PASSED                                   [100%]
​ 	
​ 	========================== 2 passed in 0.01s ===========================
``` 
And to run just the slow tests, use ``-m slow --slow``:
```bash
​ 	​$ ​​pytest​​ ​​-v​​ ​​-m​​ ​​slow​​ ​​--slow​
​ 	========================= test session starts ==========================
​ 	collected 2 items / 1 deselected / 1 selected
​ 	
​ 	test_slow.py::test_slow PASSED                                   [100%]
​ 	
​ 	=================== 1 passed, 1 deselected in 0.01s ====================
```
We have now created a local conftest plugin. Because it’s entirely contained in a ``conftest.py`` file, we can use it as is. However, packaging it as an installable plugin will make it easier to share with other projects.

## Creating an Installable Plugin
In this section, we’ll walk through the process of going from local conftest plugin to installable plugin. Even if you never put your own plugins up on PyPI, it’s good to walk through the process at least once. The experience will help you when reading code from open source plugins, and you’ll be better equipped to judge if the plugins can help you or not.

First, we need to create a new directory for our plugin code. The name of the top-level directory doesn’t really matter. We’ll call it ``pytest_skip_slow``:
```bash
​ 	pytest_skip_slow
​ 	├── examples
​ 	│   └── test_slow.py
​ 	└── pytest_skip_slow.py
```
Here ``test_slow.py`` was moved into an ``examples`` directory. We’ll use it as-is later when automating tests for the plugin. Our ``conftest.py`` file is copied directly to ``pytest_skip_slow.py``. The name ``pytest_skip_slow.py`` also is up to you. However, use a descriptive name, as the file will end up in our virtual environments ``site-packages`` directory when we ``pip install`` it later.

Now we need to create some Python packaging-specific files for the project. Specifically, we need to fill in a ``pyproject.toml`` file, a ``LICENSE`` file, and a README.md. We’ll use Flit to help us with the ``pyproject.toml`` file and ``LICENSE``. We’ll have to modify ``pyproject.toml``, but Flit will give us a good start on it. Then we’ll have to write our own ``README.md``. We’re choosing Flit because it’s easy, and the Cards project also uses it.

We start by installing Flit and running flit init inside a virtual environment and in the new directory:
```bash
​ 	​$ ​​cd​​ ​​path/to/code/ch15/pytest_skip_slow​
​ 	​$ ​​pip​​ ​​install​​ ​​flit​
​ 	​$ ​​flit​​ ​​init​
​ 	Module name [pytest_skip_slow]:
​ 	Author: Your Name
​ 	Author email: your.name@example.com
​ 	Home page: https://github.com/okken/pytest-skip-slow
​ 	Choose a license (see https://choosealicense.com/ for more info)
​ 	1. MIT - simple and permissive
​ 	2. Apache - explicitly grants patent rights
​ 	3. GPL - ensures that code based on this is shared with the same terms
​ 	4. Skip - choose a license later
​ 	Enter 1-4: 1
​ 	
​ 	Written pyproject.toml; edit that file to add optional extra info.
```
``flit init`` asks you a handful of questions. Answer the best you can. For example, “Home page” is required for ``flit init``, but I often don’t know what to put there. For projects that I have no intent on publishing to GitHub or PyPI, I fill this field in with my company URL, my blog site, or whatever.

Let’s now look at what ``pyproject.toml`` looks like right after ``flit init``:
```toml
​ 	​[build-system]​
​ 	requires = [​"flit_core >=3.2,<4"​]
​ 	build-backend = ​"flit_core.buildapi"​
​ 	
​ 	​[project]​
​ 	name = ​"pytest_skip_slow"​
​ 	authors = [​{name​ ​=​ ​"Your Name"​, ​email​ ​=​ ​"your.name@example.com"​​}​]
​ 	classifiers = [​"License :: OSI Approved :: MIT License"​]
​ 	dynamic = [​"version"​, ​"description"​]
​ 	
​ 	​[project.urls]​
​ 	Home = ​"https://github.com/okken/pytest-skip-slow"​
```
This isn’t correct yet. The defaults are a good start, but we need to modify it for pytest plugins.

Here’s the final ``pyproject.toml``:

[ch15/pytest_skip_slow_final/pyproject.toml](./pytest_skip_slow_final/pyproject.toml)
```toml
​ 	​[build-system]​
​ 	requires = [​"flit_core >=3.2,<4"​]
​ 	build-backend = ​"flit_core.buildapi"​
​ 	
​ 	​[project]​
​ 	name = ​"pytest-skip-slow"​
​ 	authors = [​{name​ ​=​ ​"Your Name"​, ​email​ ​=​ ​"your.name@example.com"​​}​]
​ 	readme = ​"README.md"​
​ 	classifiers = [
​ 	    ​"License :: OSI Approved :: MIT License"​,
​ 	    ​"Framework :: Pytest"​
​ 	]
​ 	dynamic = [​"version"​, ​"description"​]
​ 	dependencies = ​["pytest>=6.2.0"]​
​ 	requires-python = ​">=3.7"​
​ 	
​ 	​[project.urls]​
​ 	Home = ​"https://github.com/okken/pytest-skip-slow"​
​ 	
​ 	​[project.entry-points.pytest11]​
​ 	skip_slow = ​"pytest_skip_slow"​
​ 	
​ 	​[project.optional-dependencies]​
​ 	test = ​["tox"]​
​ 	
​ 	​[tool.flit.module]​
​ 	name = ​"pytest_skip_slow"​
```
What changed:
* ``name`` is changed to ``"pytest-skip-slow"``. Flit assumes the module name and package name will be the same. That’s not true of pytest plugins. pytest plugins usually start with ``pytest-`` and Python doesn’t like module names with dashes.
* The actual name of the module is set in the ``[tool.flit.module]`` section with ``name = "pytest_skip_slow"``. This module name will also show up in the ``entry-points`` section.
* The section ``[project.entry-points.pytest11]`` is added, with one entry ``pytest_skip_slow = "pytest_skip_slow.py"``. This section name is always the same for pytest plugins. It’s defined by [pytest](https://docs.pytest.org/en/latest/how-to/writing_plugins.html#making-your-plugin-installable-by-others). The section needs one entry, ``name_of_plugin = "plugin_module"``. In our case, this is ``skip_slow = "pytest_skip_slow"``.
* The `classifiers` section has been extended to include `"Framework :: Pytest"`, a special classifier specifically for pytest plugins.
* `readme` points to our `README.md` file, which we haven’t written yet. It’s optional, but weird to not have one.
* `dependencies` lists dependencies. Because pytest plugins require pytest, we list pytest. We’ve specified it with a requirement that pytest must be version 6.2.0 or above. Pinning the pytest version is optional, but I like to specify the versions I specifically test against. Start with the pytest version you are using. Then expand to older versions if you’ve tested against them and they work.
* `requires-python` is optional. However, I only intend to test against Python versions 3.7 and above.
* Section `[project.optional-dependencies], test = [ "tox" ]` is also optional. When we test our plugin, we’re going to want pytest and tox. pytest is already part of the `dependencies`, but tox is not. Setting `test = [ "tox" ]` tells Flit to install tox when we install our project in editable mode.

Check out the Flit documentation for a good write-up of all you can put in [pyproject.toml](https://flit.readthedocs.io/en/latest/pyproject_toml.html).

We’re almost ready to build our package. However, there are still a few things missing. We still need to:
1. Add a docstring describing the plugin to the top of `pytest_skip_slow.py`.
2. Add a `__version__` string to `pytest_skip_slow.py`.
3. Create a `README.md` file. (It doesn’t have to be fancy; we can add to it later.)

Luckily, at this point, if we try to run `flit build` without some of these items, Flit will tell us what’s missing.

Here’s a docstring and version in `pytest_skip_slow.py`:

[ch15/pytest_skip_slow_final/pytest_skip_slow.py](./pytest_skip_slow_final/pytest_skip_slow.py)
```python
​ 	​"""​
​ 	​A pytest plugin to skip `@pytest.mark.slow` tests by default.​
​ 	​Include the slow tests with `--slow`.​
​ 	​"""​
​ 	
​ 	​import​ ​pytest​
​ 	
​ 	__version__ = ​"0.0.1"​
​ 	
​ 	​# ... the rest of our plugin code ...​
```
And a simple starter README.md:

[ch15/pytest_skip_slow_final/README.md](./pytest_skip_slow_final/README.md)
```md
​ 	# pytest-skip-slow
​ 	
​ 	A pytest plugin to skip ​`@pytest.mark.slow`​ tests by default.
​ 	Include the slow tests with ​`--slow`​.
```
Now we can use `flit build` to build an installable package:
```bash
​ 	​$ ​​flit​​ ​​build​
​ 	Built sdist: dist/pytest-skip-slow-0.0.1.tar.gz             I-flit_core.sdist
​ 	Copying package file(s) from .../pytest_skip_slow.py        I-flit_core.wheel
​ 	Writing metadata files                                      I-flit_core.wheel
​ 	Writing the record of files                                 I-flit_core.wheel
​ 	Built wheel: dist/pytest_skip_slow-0.0.1-py3-none-any.whl   I-flit_core.wheel
```
Woohoo! We have an installable wheel. Now we can do whatever we want with it. We can email the ``.whl`` file to someone to try out. We can install the wheel directly to try it out ourselves:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​dist/pytest_skip_slow-0.0.1-py3-none-any.whl​
​ 	Processing ./dist/pytest_skip_slow-0.0.1-py3-none-any.whl
​ 	​...​
​ 	Installing collected packages: pytest-skip-slow
​ 	Successfully installed pytest-skip-slow-0.0.1
​ 	​$ ​​pytest​​ ​​examples/test_slow.py​
​ 	========================= test session starts ==========================
​ 	collected 2 items
​ 	
​ 	examples/test_slow.py .s                                         [100%]
​ 	
​ 	===================== 1 passed, 1 skipped in 0.01s =====================
​ 	​$ ​​pytest​​ ​​--slow​​ ​​examples/test_slow.py​
​ 	========================= test session starts ==========================
​ 	collected 2 items
​ 	
​ 	examples/test_slow.py ..                                         [100%]
​ 	
​ 	========================== 2 passed in 0.00s ===========================
```
Sweet. It works.

If we want to stop here, there are a few more steps you should remember to do:
* Make sure `__pycache__` and dist are ignored by your version control system. For Git, add these to `.gitignore`.
* Commit `LICENSE, README.md, pyproject.toml, examples/test_slow.py`, and `pytest_skip_slow.py`.

However, we’re not going to stop here. In the next sections we’re going to add tests and walk through publishing the plugin.
## Testing Plugins with pytester
Plugins are code that needs to be tested just like any other code. However, testing a change to a testing tool is a little tricky. When we tested the plugin manually with `test_slow.py`, we
* ran with `-v` to make sure the slow marked test was skipped,
* ran with `-v --slow` to make sure both tests ran, and
* ran with `-v -m slow --slow` to make sure just the slow test ran.

We’re going to automate those tests with the help of a plugin called `pytester`. `pytester` ships with pytest but is disabled by default. The first thing we need to do then, is to enable it in `conftest.py`:

[ch15/pytest_skip_slow_final/tests/conftest.py](./pytest_skip_slow_final/tests/conftest.py)
```python
​ 	pytest_plugins = [​"pytester"​]
```
Now we can use `pytester` to write our test cases. `pytester` creates a temporary directory for each test that uses the `pytester` fixture. The `pytester` [documentation](https://docs.pytest.org/en/latest/reference/reference.html#std-fixture-pytester) lists a bunch of functions to help populate this directory:
* `makefile()` creates a file of any kind.
* `makepyfile()` creates a python file. This is commonly used to create test files.
* `makeconftest()` creates `conftest.py`.
* `makeini()` creates a `tox.ini`.
* `makepyprojecttoml()` creates `pyproject.toml`.
* `maketxtfile()` … you get the picture.
* `mkdir()` and `mkpydir()` create test subdirectories with or without `__init__.py`.
* `copy_example()` copies files from the project’s directory to the temporary directory. This is my favorite and what we’ll be using for testing our plugin.

After we have our temporary directory populated, we can `runpytest()`, which returns a [`RunResult` object](https://docs.pytest.org/en/latest/reference/reference.html#pytest.RunResult). With the result, we can check the outcome of the test run and examine the output.

Let’s look at an example:

[ch15/pytest_skip_slow_final/tests/test_plugin.py](./pytest_skip_slow_final/tests/test_plugin.py)
```python
​ 	​import​ ​pytest​
​ 	
​ 	
​ 	@pytest.fixture()
​ 	​def​ ​examples​(pytester):
​ 	    pytester.copy_example(​"examples/test_slow.py"​)
​ 	
​ 	
​ 	​def​ ​test_skip_slow​(pytester, examples):
​ 	    result = pytester.runpytest(​"-v"​)
​ 	    result.stdout.fnmatch_lines(
​ 	        [
​ 	            ​"*test_normal PASSED*"​,
​ 	            ​"*test_slow SKIPPED (need --slow option to run)*"​,
​ 	        ]
​ 	    )
​ 	    result.assert_outcomes(passed=1, skipped=1)
```
`copy_example()` copies our example `test_slow.py` into the temporary directory we’re using for testing. I’ve put the `copy_example()` call into the `examples` fixture so it can be reused in all of the tests. This is just to keep the tests a bit cleaner by moving common setup out of the individual tests. The `examples` directory is in our project directory, which is what `copy_example()` uses as its top directory. That can be changed by setting `pytester_example_dir` in our project settings file. However, I like the explicitness of leaving the relative path in the `copy_example()` call.

`test_skip_slow()` calls `runpytest("-v")` to run pytest with `-v`. `runpytest()` returns a result, which allows us to examine `stdout` and `assert_outcomes()`. There are a bunch of ways to look at `stdout`, but I find `fnmatch_lines()` the handiest. The name comes from the fact that it’s based on fnmatch from [the standard library](https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch). We provide `fnmatch_lines()` with a list of lines that we want matched, in relative order. The * is a wildcard and is rather important to get any reasonable results from it.

The outcomes can be checked with `assert_outcomes()`, which has you pass in the expected outcomes and does the assert for you, or `parseoutcomes()`. `parseoutcomes()` returns a dictionary of outcomes. We can then assert ourselves against that. We’ll use `parseoutcomes()` in one of our tests, to see how that works.

Let’s look at the next test:

[ch15/pytest_skip_slow_final/tests/test_plugin.py](./pytest_skip_slow_final/tests/test_plugin.py)
```python
​ 	​def​ ​test_run_slow​(pytester, examples):
​ 	    result = pytester.runpytest(​"--slow"​)
​ 	    result.assert_outcomes(passed=2)
```

Well, dang, that’s simple. We’re reusing the `examples` fixture to copy `test_slow.py`. So we just need to run pytest with `--slow` and assert that both tests pass. Why don’t we need to look at the output with `fnmatch_lines()`? We could do that. However, there are only two tests, so if two pass, there’s not really much else to test. I used `fnmatch_lines` in the first test to make sure the expected test was passing and the expected test was skipped.

Let’s use `parseoutcomes()` in the next test (mostly so that there’s something new to learn):

[ch15/pytest_skip_slow_final/tests/test_plugin.py](./pytest_skip_slow_final/tests/test_plugin.py)
```python
​ 	​def​ ​test_run_only_slow​(pytester, examples):
​ 	    result = pytester.runpytest(​"-v"​, ​"-m"​, ​"slow"​, ​"--slow"​)
​ 	    result.stdout.fnmatch_lines([​"*test_slow PASSED*"​])
​ 	    outcomes = result.parseoutcomes()
​ 	    ​assert​ outcomes[​"passed"​] == 1
​ 	    ​assert​ outcomes[​"deselected"​] == 1
```
For `test_run_only_slow()`, I’ve added back in the `-v` so we can look at the output. We have two tests and we only want to run one, the slow one. `fnmatch_lines()` is being used to make sure it’s the correct test.

The `parseoutcomes()` call returns a dictionary that we can assert against. In this case, we want one `’passed’` test and one `’deselected’`.

Now just for fun, let’s make sure our help text shows up with `--help`:

[ch15/pytest_skip_slow_final/tests/test_plugin.py](./pytest_skip_slow_final/tests/test_plugin.py)
```python
​ 	​def​ ​test_help​(pytester):
​ 	    result = pytester.runpytest(​"--help"​)
​ 	    result.stdout.fnmatch_lines(
​ 	        [​"*--slow * include tests marked slow*"​]
​ 	    )
```
That’s pretty good behavior coverage for our plugin.

Before we run this, let’s test against the editable code:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch15/pytest_skip_slow_final​
​ 	​$ ​​pip​​ ​​uninstall​​ ​​pytest-skip-slow​
​ 	​$ ​​pip​​ ​​install​​ ​​-e​​ ​​.​
```
The dot ( . ) in `pip install -e` . means the current directory. Remember that pip needs to be version 21.3 or later for this to work.

Now we know we’re testing the same code we’re looking at.
```bash
​ 	​$ ​​pytest​​ ​​-v​
​ 	========================= test session starts ==========================
​ 	collected 4 items
​ 	
​ 	tests/test_plugin.py::test_skip_slow PASSED                      [ 25%]
​ 	tests/test_plugin.py::test_run_slow PASSED                       [ 50%]
​ 	tests/test_plugin.py::test_run_only_slow PASSED                  [ 75%]
​ 	tests/test_plugin.py::test_help PASSED                           [100%]
​ 	
​ 	========================== 4 passed in 0.20s ===========================
```
Cool. Looking good. Next, let’s use tox to test our plugin against a few Python versions.

## Testing Multiple Python and pytest Versions with tox
In Chapter 11, [​tox and Continuous Integration](../ch11/README.md#tox-and-continuous-integration)​, we used tox to test Cards against multiple versions of Python. We’re going to do the same thing with our plugin, but also test against a couple versions of pytest.

Here’s our `tox.ini` for our plugin:

[ch15/pytest_skip_slow_final/tox.ini](./pytest_skip_slow_final/tox.ini)
```ini
​ 	​[pytest]​
​ 	testpaths = ​tests​
​ 	
​ 	​[tox]​
​ 	envlist = ​py{37, 38, 39, 310}-pytest{62,70}​
​ 	isolated_build = ​True​
​ 	
​ 	​[testenv]​
​ 	deps =
​ 	    ​pytest62:​ pytest=​=6.2.5​
​ 	    ​pytest70:​ pytest=​=7.0.0​
​ 	
​ 	commands = ​pytest {posargs:tests}​
​ 	description = ​Run pytest​
```
We are using a couple of new tricks for tox:
* `envlist = py{37, 38, 39, 310}-pytest{62,70}`. The curly brackets and dashes are creating a test environment matrix. This is a shorthand that tells tox to create environments for all combinations of the four listed versions of Python and the two listed versions of pytest. See [tox docs](https://tox.wiki/en/latest/example/basic.html#compressing-dependency-matrix) for more information.
* The `deps` section has two rows, `pytest62: pytest==6.2.5` and `pytest70: pytest==7.0.0`. This tells tox that for every environment that ends with `-pytest62`, it should install pytest 6.2.5. Likewise, for `-pytest70` environments, install pytest 7.0.0.

And now we just run it:
```bash
​ 	​$ ​​tox​​ ​​-q​​ ​​--parallel​
​ 	​...​
​ 	_______________________________ summary ________________________________
​ 	  py37-pytest62: commands succeeded
​ 	  py37-pytest70: commands succeeded
​ 	  py38-pytest62: commands succeeded
​ 	  py38-pytest70: commands succeeded
​ 	  py39-pytest62: commands succeeded
​ 	  py39-pytest70: commands succeeded
​ 	  py310-pytest62: commands succeeded
​ 	  py310-pytest70: commands succeeded
​ 	  congratulations :)
```
The `-q` reduces the output of tox, and `--parallel` tells tox to run the environments in parallel. Since the 4x2 matrix creates eight test environments, running them in parallel saves a bit of time.

Now let’s move on to publishing.
## Publishing Plugins
Now that we have a plugin built and tested, we’d like to share it with other projects, our company, or even the world. Bwahahahaha!

To publish your plugin, you can:
* Push your plugin code to a Git repository and install from there.
   * For example: `pip install git+https://github.com/okken/pytest-skip-slow`
   * Note that you can list multiple `git+https://...` repositories in a `requirements.txt` file and as dependencies in `tox.ini`.
* Copy the wheel, `pytest_skip_slow-0.0.1-py3-none-any.whl`, to a shared directory somewhere and install from there.
   * `cp dist/*.whl path/to/my_packages/`
   * `pip install pytest-skip-slow --no-index --find-links=path/to/my_packages/`
* Publish to PyPI.
   * Check out the Uploading the [distribution archives](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) section in Python’s documentation on packaging.
   * Also see the Controlling [package uploads](https://flit.readthedocs.io/en/latest/upload.html#controlling-package-uploads) section of the Flit documentation.
# Review
Wow. In this chapter, we created a plugin and left it inches away from being able to push it to PyPI. We looked at how to move from hook functions in a ``conftest.py`` file to an installable and distributable packaged pytest plugin.

In addition, we
* used a ``conftest.py`` and simple test code to manually develop hook functions for our plugin;
* moved ``conftest.py`` code into a new directory and `pytest_skip_slow.py`;
* moved test code into an examples directory;
* used `flit init` to create a `pyproject.toml` file, then modified the file for the special needs of pytest plugins;
* tried building with `flit build` and manually testing with `built wheel`;
* developed test code that utilized `pytester` and an example test file; and
* looked at different ways to distribute a package.       
## Exercises
Walking through the steps to go from `pytest-skip-slow` to `pytest-skip-slow-full` will help you learn how to build and test a plugin.

The supplied source code includes the following:
* `local` (the local conftest plugin)
* `pytest-skip-slow` (just the copy from local into new names)
* `pytest-skip-slow-full` (a possible final layout for the completed plugin)

1. Try out `-v`, `--slow`, and `-v -m slow --slow` in the `local` directory.
2. Go to the `pytest-skip-slow` directory.
3. `pip install flit` and run `flit init`. Use your own information.
4. Modify the `pyproject.toml` file as described in the chapter.
5. Run `flit build` and try out the generated wheel.
6. Add tests and a `tox.ini` file to run tests with either `pytest` or `tox`.
7. (Bonus) Create a plugin with a fixture, instead of hook functions. Especially within teams or a large project, using common fixtures can really speed up test development. The fixture could be something that returns interesting data, or fake data, or a connection to a temporary database, filled or empty. This really could be anything. Try to make it useful for something you are interested in or useful for a project you are working on.