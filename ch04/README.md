# Chapter 4 Builtin Fixtures
In the previous chapter, you learned what fixtures are, how to write them, and how to use them for test data as well as setup and teardown code. You also used conftest.py for sharing fixtures between tests in multiple test files.

Reusing common fixtures is such a good idea that the pytest developers included some commonly used fixtures with pytest. The builtin fixtures that come prepackaged with pytest can help you do some pretty useful things in your tests easily and consistently. For example, pytest includes builtin fixtures that can handle temporary directories and files, access command-line options, communicate between test sessions, validate output streams, modify environment variables, and interrogate warnings. The builtin fixtures are extensions to the core functionality of pytest.

We’ll take a look at a few of the builtin fixtures in this chapter:
* `tmp_path` and `tmp_path_factory`—for temporary directories
* `capsys`—for capturing output
* `monkeypatch`—for changing the environment or application code, like a lightweight form of mocking

This is a good mix that shows you some of the extra capabilities you can get with creative fixture use. I encourage you to read up on other builtin fixtures by reading the output of `pytest --fixtures`.

## Using tmp_path and tmp_path_factory
The `tmp_path` and `tmp_path_factory` fixtures are used to create temporary directories. The `tmp_path` function-scope fixture returns a `pathlib`.`Path` instance that points to a temporary directory that sticks around during your test and a bit longer. The `tmp_path_factory` session-scope fixture returns a `TempPathFactory` object. This object has a `mktemp()` function that returns Path objects. You can use `mktemp()` to create multiple temporary directories.

You use them like this:

[ch4/test_tmp.py](./test_tmp.py)
```python
​ 	​def​ ​test_tmp_path​(tmp_path):
​ 	    file = tmp_path / ​"file.txt"​
​ 	    file.write_text(​"Hello"​)
​ 	    ​assert​ file.read_text() == ​"Hello"​
​ 	
​ 	
​ 	​def​ ​test_tmp_path_factory​(tmp_path_factory):
»	    path = tmp_path_factory.mktemp(​"sub"​)
​ 	    file = path / ​"file.txt"​
​ 	    file.write_text(​"Hello"​)
​ 	    ​assert​ file.read_text() == ​"Hello"
```
​
Their usage is almost identical except for the following:
* With `tmp_path_factory`, you have to call `mktemp()` to get a directory.
* `tmp_path_factory` is session scope.
* `tmp_path` is function scope.

In the previous chapter, we used the standard library `tempfile`.`TemporaryDirectory` for our db fixture:

[ch4/conftest_from_ch3.py](./conftest_from_ch3.py)
```python
​ 	​from​ ​pathlib​ ​import​ Path
​ 	​from​ ​tempfile​ ​import​ TemporaryDirectory
​ 	
​ 	
​ 	@pytest.fixture(scope=​"session"​)
​ 	​def​ ​db​():
​ 	    ​"""CardsDB object connected to a temporary database"""​
​ 	    ​with​ TemporaryDirectory() ​as​ db_dir:
​ 	        db_path = Path(db_dir)
​ 	        db_ = cards.CardsDB(db_path)
​ 	        ​yield​ db_
​ 	        db_.close()
```
Let’s use one of the new builtins instead. Because our `db` fixture is session scope, we cannot use `tmp_path`, as session-scope fixtures cannot use function-scope fixtures. We can use `tmp_path_factory`:

[ch4/conftest.py](./conftest.py?plain=1#L5-L11)
```python
​ 	@pytest.fixture(scope=​"session"​)
​ 	​def​ ​db​(tmp_path_factory):
​ 	    ​"""CardsDB object connected to a temporary database"""​
​ 	    db_path = tmp_path_factory.mktemp(​"cards_db"​)
​ 	    db_ = cards.CardsDB(db_path)
​ 	    ​yield​ db_
​ 	    db_.close()
```
Nice. Notice that this also allows us to remove two import statements, as we don’t need to import `pathlib` or `tempfile`.

Following are two related builtin fixtures:
* `*tmpdir`—Similar to `tmp_path`, but returns a `py.path.local` object. This fixture was available in pytest long before `tmp_path`. `py.path.local` predates pathlib, which was added in Python 3.4. `py.path.local` is being phased out slowly in pytest in favor of the stdlib pathlib version. Therefore, I recommend using `tmp_path`.
* `tmpdir_factory`—Similar to `tmp_path_factory`, except its `mktemp` function returns a `py.path.local` object instead of a `pathlib.Path` object

The base directory for all of the pytest temporary directory fixtures is system- and user-dependent, and includes a `pytest-NUM` part, where `NUM` is incremented for every session. The base directory is left as-is immediately after a session to allow you to examine it in case of test failures. pytest does eventually clean them up. Only the most recent few temporary base directories are left on the system.

You can also specify your own base directory if you need to with `pytest --basetemp=mydir`.
## Using capsys
Sometimes the application code is supposed to output something to `stdout`, `stderr`, and so on. As it happens, the Cards sample project has a command-line interface that should be tested.

The command, `cards version`, is supposed to output the version:
```bash
​ 	​$ ​​cards​​ ​​version​
​ 	1.0.0
```
The version is also available from the API:
```bash
​ 	​$ ​​python​​ ​​-i​
​ 	​>>>​​ ​​import​​ ​​cards​
​ 	​>>>​​ ​​cards.__version__​
​ 	'1.0.0'
```
One way to test this would be to actually run the command with `subprocess.run()`, grab the output, and compare it to the version from the API:

[ch4/test_version.py](./test_version.py)
```python
​ 	​import​ ​subprocess​
​ 	
​ 	
​ 	​def​ ​test_version_v1​():
​ 	    process = subprocess.run(
​ 	        [​"cards"​, ​"version"​], capture_output=True, text=True
​ 	    )
​ 	    output = process.stdout.rstrip()
​ 	    ​assert​ output == cards.__version__
```
The `rstrip()` is used to remove the newline. (I started with this example because sometimes calling a subprocess and reading the output is your only option. However, it makes a lousy `capsys` example.)

The `capsys` fixture enables the capturing of writes to `stdout` and `stderr`. We can call the method that implements this in the CLI directly, and use `capsys` to read the output:

[ch4/test_version.py](./test_version.py)
```python
​ 	​import​ ​cards​
​ 	
​ 	
​ 	​def​ ​test_version_v2​(capsys):
​ 	    cards.cli.version()
​ 	    output = capsys.readouterr().out.rstrip()
​ 	    ​assert​ output == cards.__version__
```
The `capsys.readouterr()` method returns a namedtuple that has `out` and `err`. We’re just reading the out part and then stripping the newline with `rstrip()`.

Another feature of `capsys` is the ability to temporarily disable normal output capture from pytest. pytest usually captures the output from your tests and the application code. This includes print statements.

Here’s a small example:

[ch4/test_print.py](./test_print.py)
```python
​ 	​def​ ​test_normal​():
​ 	    ​print​(​"​​\n​​normal print"​)
```
If we run it, we don’t see any output:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch4​
​ 	​$ ​​pytest​​ ​​test_print.py::test_normal​
​ 	======================= test session starts =======================
​ 	collected 1 item
​ 	
​ 	test_print.py .                                             [100%]
​ 	
​ 	======================== 1 passed in 0.00s ========================
```
pytest captures all the output. It helps keep the command-line session cleaner.

However, there may be times when we want to see all the output, even on passing tests. We can use the `-s` or `--capture=no` flag for that:
```bash
​ 	​$ ​​pytest​​ ​​-s​​ ​​test_print.py::test_normal​
​ 	======================= test session starts =======================
​ 	collected 1 item
​ 	
​ 	test_print.py
»	normal print
​ 	.
​ 	
​ 	======================== 1 passed in 0.00s ========================
```
pytest will then show the output for tests that fail, at the end.

Here’s a simple failing test:

[ch4/test_print.py](./test_print.py)
```python
​ 	​def​ ​test_fail​():
​ 	    ​print​(​"​​\n​​print in failing test"​)
​ 	    ​assert​ False
```
The output is shown:
```bash
​ 	​$ ​​pytest​​ ​​test_print.py::test_fail​
​ 	======================= test session starts =======================
​ 	collected 1 item
​ 	
​ 	test_print.py F                                             [100%]
​ 	
​ 	============================ FAILURES =============================
​ 	____________________________ test_fail ____________________________
​ 	
​ 	    def test_fail():
​ 	        print("\nprint in failing test")
​ 	​>​​       ​​assert​​ ​​False​
​ 	E       assert False
​ 	
​ 	test_print.py:9: AssertionError
»	---------------------- Captured stdout call -----------------------
»	
»	print in failing test
​ 	===================== short test summary info =====================
​ 	FAILED test_print.py::test_fail - assert False
​ 	======================== 1 failed in 0.04s ========================
```
Another way to always include output is with `capsys.disabled()`:

[ch4/test_print.py](./test_print.py)
```python
​ 	​def​ ​test_disabled​(capsys):
​ 	    ​with​ capsys.disabled():
​ 	        ​print​(​"​​\n​​capsys disabled print"​)
```
The output in the with block will always be displayed, even without the -s flag:
```bash
​ 	​$ ​​pytest​​ ​​test_print.py::test_disabled​
​ 	======================= test session starts =======================
​ 	collected 1 item
​ 	
​ 	test_print.py
​ 	capsys disabled print
​ 	.                                             [100%]
​ 	
​ 	======================== 1 passed in 0.00s ========================
```
Following are related builtin fixtures:
* `capfd`—Like `capsys`, but captures file descriptors 1 and 2, which usually is the same as stdout and stderr
* `capsysbinary`—Where `capsys` captures text, `capsysbinary` captures bytes.
* `capfdbinary`—Captures bytes on file descriptors 1 and 2
* `caplog`—Captures output written with the logging package

## Using monkeypatch
During the previous discussion of `capsys`, we used this code to test the output of the Cards project:

[ch4/test_version.py](./test_version.py)
```python
​ 	​import​ ​cards​
​ 	
​ 	
​ 	​def​ ​test_version_v2​(capsys):
​ 	    cards.cli.version()
​ 	    output = capsys.readouterr().out.rstrip()
​ 	    ​assert​ output == cards.__version__
```
That made a decent example of how to use `capsys`, but it’s still not how I prefer to test the CLI. The Cards application uses a library called [Typer](
https://pypi.org/project/typer) that includes a runner feature that allows us to test more of our code, makes it look more like a command-line test, remains in process, and provides us with output hooks. It’s used like this:

[ch4/test_version.py](./test_version.py)
```python
​ 	​from​ ​typer.testing​ ​import​ CliRunner
​ 	
​ 	
​ 	​def​ ​test_version_v3​():
​ 	    runner = CliRunner()
​ 	    result = runner.invoke(cards.app, [​"version"​])
​ 	    output = result.output.rstrip()
​ 	    ​assert​ output == cards.__version__
```
We’ll use this method of output testing as a starting point for the rest of the tests we do of the Cards CLI.

I started the CLI testing by testing `cards version`. Starting with `cards version` is nice because it doesn’t use the database. In order to test the rest of the CLI, we need to redirect the database to a temporary directory, like we did when testing the API in ​[Using Fixtures for Setup and Teardown](../ch03/README.md#using-fixtures-for-setup-and-teardown)​. We’ll use `monkeypatch` for that.

A “monkey patch” is a dynamic modification of a class or module during runtime. During testing, “monkey patching” is a convenient way to take over part of the runtime environment of the application code and replace either input dependencies or output dependencies with objects or functions that are more convenient for testing. The `monkeypatch` builtin fixture allows you to do this in the context of a single test. It is used to modify objects, dictionaries, environment variables, the python search path, or the current directory. It’s like a mini version of mocking. And when the test ends, regardless of pass or fail, the original unpatched code is restored, undoing everything changed by the patch.

This is all very hand-wavy until we jump into some examples. After looking at the API, we’ll look at how `monkeypatch` is used in test code.

The `monkeypatch` fixture provides the following functions:
* `setattr(target, name, value, raising=True)`—Sets an attribute
* `delattr(target, name, raising=True)`—Deletes an attribute
* `setitem(dic, name, value)`—Sets a dictionary entry
* `delitem(dic, name, raising=True)`—Deletes a dictionary entry
* `setenv(name, value, prepend=None)`—Sets an environment variable
* `delenv(name, raising=True)`—Deletes an environment variable
* `syspath_prepend(path)`—Prepends `path` to `sys.path`, which is Python’s list of import locations
* `chdir(path)`—Changes the current working directory

The `raising` parameter tells pytest whether or not to raise an exception if the item doesn’t already exist. The prepend parameter to `setenv()` can be a character. If it is set, the value of the environment variable will be changed to `value + prepend + <old value>`.

We can use `monkeypatch` to redirect the CLI to a temporary directory for the database in a couple of ways. Both methods involve knowledge of the application code. Let’s look at the `cli.get_path()` method:

[cards_proj/src/cards/cli.py](../cards_proj/src/cards/cli.py?plain=1#L126-L132)
```python
def get_path():
    db_path_env = os.getenv("CARDS_DB_DIR", "")
    if db_path_env:
        db_path = pathlib.Path(db_path_env)
    else:
        db_path = pathlib.Path.home() / "cards_db"
    return db_path
``` 
This is the method that tells the rest of the CLI code where the database is. We can either patch the whole function, patch `pathlib.Path().home()`, or set the environment variable `CARDS_DB_DIR`.

We’ll test these modifications with the `cards config` command, which conveniently returns the database location:
```bash
​ 	​$ ​​cards​​ ​​config​
​ 	/Users/okken/cards_db
```
Before we jump in, we’re going to be calling `runner.invoke()` to call `cards` several times, so let’s put that code into a helper function called `run_cards()`:

[ch4/test_config.py](./test_config.py)
```python
​ 	​from​ ​typer.testing​ ​import​ CliRunner
​ 	​import​ ​cards​
​ 	
​ 	
​ 	​def​ ​run_cards​(*params):
​ 	    runner = CliRunner()
​ 	    result = runner.invoke(cards.app, params)
​ 	    ​return​ result.output.rstrip()
​ 	
​ 	
​ 	​def​ ​test_run_cards​():
​ 	    ​assert​ run_cards(​"version"​) == cards.__version__
```
Notice that I included a test function for our helper function, just to make sure I got it right.

First, let’s try patching the entire `get_path` function:

[ch4/test_config.py](./test_config.py)
```python
​ 	​def​ ​test_patch_get_path​(monkeypatch, tmp_path):
​ 	    ​def​ ​fake_get_path​():
​ 	        ​return​ tmp_path
​ 	
​ 	    monkeypatch.setattr(cards.cli, ​"get_path"​, fake_get_path)
​ 	    ​assert​ run_cards(​"config"​) == str(tmp_path)
```
Like mocking, monkey-patching requires a bit of a mind shift to get everything set up right. The function, `get_path` is an attribute of cards.cli. We want to replace it with `fake_get_path`. Because `get_path` is a callable function, we have to replace it with another callable function. We can’t just replace it with `tmp_path`, which is a `pathlib.Path` object that is not callable.

If we want to instead replace the `home()` method in `pathlib.Path`, it’s a similar patch:

[ch4/test_config.py](./test_config.py?plain=1#L23-L30)
```python
​ 	​def​ ​test_patch_home​(monkeypatch, tmp_path):
​ 	    full_cards_dir = tmp_path / ​"cards_db"​
​ 	
​ 	    ​def​ ​fake_home​():
​ 	        ​return​ tmp_path
​ 	
​ 	    monkeypatch.setattr(cards.cli.pathlib.Path, ​"home"​, fake_home)
​ 	    ​assert​ run_cards(​"config"​) == str(full_cards_dir)
```
Because `cards.cli` is importing `pathlib`, we have to patch the home attribute of `cards.cli.pathlib.Path`.

Seriously, if you start using monkey-patching and/or mocking more, a couple things will happen:
* You’ll start to understand this.
* You’ll start to avoid mocking and monkey-patching whenever possible.

Let’s hope the environment variable patch is less complicated:

[ch4/test_config.py](./test_config.py)
```python
​ 	​def​ ​test_patch_env_var​(monkeypatch, tmp_path):
​ 	    monkeypatch.setenv(​"CARDS_DB_DIR"​, str(tmp_path))
​ 	    ​assert​ run_cards(​"config"​) == str(tmp_path)
```

Well, look at that. It is less complicated. However, I cheated. I’ve set the code up so that this environment variable is essentially part of the Cards API so that I could use it during testing.

> ### Design for Testability
>> Designing for testability is a concept borrowed from hardware designers, specifically those developing integrated circuits. The concept is simply that you add functionality to software to make it easier to test. In some cases, it may mean undocumented API or parts of the API that are turned off for release. In other cases, the API is extended and made public.
>>
>> In the case of the Cards `config` command that returns the database location and the support of `CARDS_DB_DIR` environment variable, these were added expressly to make the code easier to test. They may also be useful to end users. At the very least, they are not harmful for users to know about, so they were left as part of the public API.
## Remaining Builtin Fixtures
In this chapter, we’ve looked at the `tmp_path`, `tmp_path_factory`, `capsys`, and `monkeypatch` builtin fixtures. There are quite a few more. Some we will discuss in other parts of the book. Others are left as an exercise for the reader to research if you find the need for them.

Here’s a list of the remaining builtin fixtures that come with pytest, as of the writing of this edition:
* `capfd`, `capfdbinary`, `capsysbinary`—Variants of `capsys` that work with file descriptors and/or binary output
* `caplog`—Similar to `capsys` and the like; used for messages created with Python’s logging system
* `cache`—Used to store and retrieve values across pytest runs. The most useful part of this fixture is that it allows for `--last-failed`, `--failed-first`, and similar flags.
* `doctest_namespace`—Useful if you like to use pytest to run doctest-style tests
* `pytestconfig`—Used to get access to configuration values, `pluginmanager`, and plugin hooks
* `record_property`, `record_testsuite_property`—Used to add extra properties to the test or test suite. Especially useful for adding data to an XML report to be used by continuous integration tools
* `recwarn`—Used to test warning messages
* `request`—Used to provide information on the executing test function. Most commonly used during fixture parametrization
* `pytester`, `testdir`—Used to provide a temporary test directory to aid in running and testing pytest plugins. pytester is the pathlib based replacement for the py.path based testdir.
* `tmpdir`, `tmpdir_factory`—Similar to `tmp_path` and `tmp_path_factory`; used to return a `py.path.local` object instead of a `pathlib.Path` object

We will take a look at many of these fixtures in the remaining chapters. You can find the full list of builtin fixtures by running `pytest --fixtures`, which also gives pretty good descriptions. You can also find more information in the [online pytest documentation](https://docs.pytest.org/en/latest/reference/fixtures.html).
## Review
In this chapter, we looked at the `tmp_path`, `tmp_path_factory`, `capsys`, and `monkeypatch` builtin fixtures:
* The `tmp_path` and `tmp_path_factory` fixtures are used to for temporary directories. tmp_path is function scope, and `tmp_path_factory` is session scope. Related fixtures not covered in the chapter are `tmpdir` and `tmpdir_factory`.
* `capsys` can be used to capture `stdout` and `stderr`. It can also be used to temporarily turn off output capture. Related fixtures are `capsysbinary`, `capfd`, `capfdbinary`, and `caplog`.
* `monkeypatch` can be used to change the application code or the environment. We used it with the Cards application to redirect the database location to a temporary directory created with `tmp_path`.
* You can read about these and other fixtures with `pytest --fixtures`.
## Exercises
Reaching for builtin fixtures whenever possible is a great way to simplify your own test code. The exercises below are designed to give you experience using `tmp_path` and `monkeypatch`, two super handy and common builtin fixtures.

Take a look at this script that writes to a file:

[ch4/hello_world.py](./hello_world.py)
```python
​ 	​def​ ​hello​():
​ 	    ​with​ open(​"hello.txt"​, ​"w"​) ​as​ f:
​ 	        f.write(​"Hello World!​​\n​​"​)
​ 	
​ 	
​ 	​if​ __name__ == ​"__main__"​:
​ 	    hello()
```
1. Write a test without fixtures that validates that `hello()` writes the correct content to `hello.txt`.
2. Write a second test using fixtures that utilizes a temporary directory and `monkeypatch.chdir()`.
3. Add a print statement to see where the temporary directory is located. Manually check the `hello.txt` file after a test run. pytest leaves the temporary directories around for a while after test runs to help with debugging.
4. Comment out the calls to `hello()` in both tests and re-run. Do they both fail? If not, why not? 
    