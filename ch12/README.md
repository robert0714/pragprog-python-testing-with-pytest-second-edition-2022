# Testing Scripts and Applications
The sample Cards application is an installable Python package that is installed with ``pip install``. Once it is installed, the test code can simply import cards to access the application’s capabilities, and test away. However, not all Python code is installable with pip, but still needs to be tested.

In this chapter, we’ll look at techniques for testing scripts and applications that cannot be installed with pip. To be clear on terms, the following definitions apply in this chapter:
* A script is a single file containing Python code that is intended to be run directly from Python, such as ``python my_script.py``.
* An importable script is a script in which no code is executed when it is imported. Code is executed only when it is run directly.
* An application refers to a package or script that has external dependencies defined in a ``requirements.txt`` file. The Cards project is also an application, but it is installed with pip. External dependencies for Cards are defined in its ``pyproject.toml`` file and pulled in during ``pip install``. In this chapter, we’ll specifically look at applications that cannot or choose to not use pip.

We’ll start with testing a script. We’ll then modify the script so that we can import it for testing. We’ll then add an external dependency and look at testing applications.

When testing scripts and applications, a few questions often come up:
* How do I run a script from a test?
* How do I capture the output from a script?
* I want to import my source modules or packages into my tests. How do I make that work if the tests and code are in different directories?
* How do I use tox if there’s no package to build?
* How do I get tox to pull in external dependencies from a ``requirements.txt`` file?

These are the questions this chapter will answer.
> ### Don’t Forget to Use a Virtual Environment  or AnaConda 
>>  **💡 Tip:** The virtual environment you’ve been using in the previous part
>  of the book can be used for the discussion in this chapter, or you can
>  create a new one. Here’s a refresher on how to do that:
>  ```bash
>  $ cd /path/to/code/ch12
>  $ python -m venv .venv
>  $ source venv/bin/activate
>  (venv) $ pip install -U pip
>  (venv) $ pip install pytest
>  (venv) $ pip install tox
>  ```
>  If in conda:
>  ```bash
>  $ cd /path/to/code/ch12
>  $ conda activate myenv
>  (myenv) $ conda config --add channels conda-forge
>  (myenv) $ conda config --set channel_priority strict
>  (myenv) $ conda install pytest pylint -c conda-forge --yes
>  (myenv) $ pip install tox-conda
>  ```

## Testing a Simple Python Script
Let’s start with the canonical coding example, Hello World!:

[ch12/script/hello.py](./script/hello.py)
```bash
​ 	​print​(​"Hello, World!"​)
```
The run output shouldn’t be surprising:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch12/script​
​ 	​$ ​​python​​ ​​hello.py​
​ 	Hello, World!
```
Like any other bit of software, scripts are tested by running them and checking the output and/or side effects.

For the ``hello.py`` script, our challenge is to (1) figure out how to run it from a test, and (2) how to capture the output. The subprocess module, which is part of [the Python standard library](https://docs.python.org/3/library/subprocess.html#subprocess.run) has a ``run()`` method that will solve both problems just fine:

[ch12/script/test_hello.py](./script/test_hello.py)
```python
from subprocess import run


def test_hello():
    result = run(["python", "hello.py"], capture_output=True, text=True)
    output = result.stdout
    assert output == "Hello, World!\n"
```

The test launches a subprocess, captures the output, and compares it to ``"Hello, World!\n"``, including the newline ``print()`` automatically adds to the output. Let’s try it out:
```bash
​ 	​$ ​​pytest​​ ​​-v​​ ​​test_hello.py​
​ 	========================= test session starts ==========================
​ 	collected 1 item
​ 	
​ 	test_hello.py::test_hello PASSED                                 [100%]
​ 	
​ 	========================== 1 passed in 0.03s ===========================
```

That’s not too bad. Let’s try it with tox.

If we set up a normal-ish ``tox.ini`` file, it won’t really work. Let’s try anyway:

[ch12/script/tox_bad.ini](./script/tox_bad.ini)
```init

​ 	​[tox]​
​ 	envlist = ​py39, py310​
​ 	
​ 	​[testenv]​
​ 	deps = ​pytest​
​ 	commands = ​pytest​
​ 	
​ 	​[pytest]​
```

Running this illustrates the problem( [tox](../ch11/README.md) ):
```bash
​ 	​$ ​​tox​​ ​​-e​​ ​​py310​​ ​​-c​​ ​​tox_bad.ini​
​ 	ERROR: No pyproject.toml or setup.py file found. The expected locations are:
​ 	  /path/to/code/ch12/script/pyproject.toml or /path/to/code/ch12/script/setup.py
​ 	You can
​ 	  1. Create one:
​ 	     https://tox.readthedocs.io/en/latest/example/package.html
​ 	  2. Configure tox to avoid running sdist:
​ 	     https://tox.readthedocs.io/en/latest/example/general.html
​ 	  3. Configure tox to use an isolated_build
```

The problem is that tox is trying to build something as the first part of its process. We need to tell tox to not try to build anything, which we can do with ``skipsdist = true``:

[ch12/script/tox.ini](./script/tox.ini)
```ini
​ 	​[tox]​
​ 	envlist = ​py39, py310​
»	skipsdist = ​true​
​ 	
​ 	​[testenv]​
​ 	deps = ​pytest​
​ 	commands = ​pytest​
​ 	
​ 	​[pytest]​
```
Now it should run fine:
```bash
   ​$ ​​tox​
​ 	​...​
​ 	py39 run-test: commands[0] | pytest
​ 	========================= test session starts ==========================
​ 	collected 1 item
​ 	
​ 	test_hello.py .                                                  [100%]
​ 	
​ 	========================== 1 passed in 0.04s ===========================
​ 	​...​
​ 	py310 run-test: commands[0] | pytest
​ 	========================= test session starts ==========================
​ 	collected 1 item
​ 	
​ 	test_hello.py .                                                  [100%]
​ 	
​ 	========================== 1 passed in 0.04s ===========================
​ 	_______________________________ summary ________________________________
​ 	  py39: commands succeeded
​ 	  py310: commands succeeded
​ 	  congratulations :)
​ 	​$
```
Awesome. We tested our script with pytest and tox and used ``subprocess.run()`` to launch our script and capture the output.

Testing a small script with ``subprocess.run()`` works okay, but it does have drawbacks. We may want to test sections of larger scripts separately. That’s not possible unless we split the functionality into functions. We also may want to separate test code and scripts into different directories. That’s also not trivial with the code as is, because our call to ``subprocess.run()`` assumed ``hello.py`` was in the same directory. A few modifications to our code can clean up these issues.

## Testing an Importable Python Script
We can change our script code a tiny bit to make it importable and allow tests and code to be in different directories. We’ll start by making sure all of the logic in the script is inside a function. Let’s move the workload of hello.py into a main() function:

[ch12/script_importable/hello.py](./script_importable/hello.py)
```python
​ 	​def​ ​main​():
​ 	    ​print​(​"Hello, World!"​)
​ 	
​ 	
​ 	​if​ __name__ == ​"__main__"​:
​ 	    main()
```

We call ``main()`` inside a if ``__name__ == ’__main__’`` block. The ``main()`` code will be called when we call the script with ``python hello.py``:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch12/script_importable​
​ 	​$ ​​python​​ ​​hello.py​
​ 	Hello, World!
```
The ``main()`` code won’t be called with just an import. We have to call ``main()`` explicitly:
```bash
​ 	​$ ​​python​
​ 	​>>>​​ ​​import​​ ​​hello​
​ 	​>>>​​ ​​hello.main()​
​ 	Hello, World!
```
Now we can test ``main()`` as if it were just any other function. In the modified test, we are using ``capsys`` (which was covered in [​Using capsys​](../ch04/README.md#using_capsys)):

[ch12/script_importable/test_hello.py](./script_importable/test_hello.py)
```python
​ 	​import​ ​hello​
​ 	
​ 	
​ 	​def​ ​test_main​(capsys):
​ 	    hello.main()
​ 	    output = capsys.readouterr().out
​ 	    ​assert​ output == ​"Hello, World!​​\n​​"​
```
Not only can we test ``main()``, but also as our script grows, we may break up code into separate functions. We can now test those functions separately. It’s a bit silly to break up Hello, World!, but let’s do it anyway, just for fun:

[ch12/script_funcs/hello.py](./script_funcs/hello.py)
```python
​ 	​def​ ​full_output​():
​ 	    ​return​ ​"Hello, World!"​
​ 	
​ 	
​ 	​def​ ​main​():
​ 	    ​print​(full_output())
​ 	
​ 	
​ 	​if​ __name__ == ​"__main__"​:
​ 	    main()
```
Here we’ve put the output contents into ``full_output()`` and the actual printing of it in ``main()``. And now we can test those separately:

[ch12/script_funcs/test_hello.py](./script_funcs/test_hello.py)
```python
​ 	​import​ ​hello​
​ 	
​ 	
​ 	​def​ ​test_full_output​():
​ 	    ​assert​ hello.full_output() == ​"Hello, World!"​
​ 	
​ 	
​ 	​def​ ​test_main​(capsys):
​ 	    hello.main()
​ 	    output = capsys.readouterr().out
​ 	    ​assert​ output == ​"Hello, World!​​\n​​"​
```
Splendid. Even a fairly large script can be reasonably tested in this manner. Now let’s look into moving our tests and scripts into separate directories.
## Separating Code into src and tests Directories
Suppose we have a bunch of scripts and a bunch of tests for those scripts, and our directory is getting a bit cluttered. So we decide to move the scripts into a ``src`` directory and the tests into a tests directory, like this:
```bash
​ 	script_src
​ 	├── src
​ 	│   └── hello.py
​ 	├── tests
​ 	│   └── test_hello.py
​ 	└── pytest.ini
```
Without any other changes, pytest will blow up:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch12/script_src​
​ 	​$ ​​pytest​​ ​​--tb=short​​ ​​-c​​ ​​pytest_bad.ini​
​ 	========================= test session starts ==========================
​ 	collected 0 items / 1 error
​ 	
​ 	================================ ERRORS ================================
​ 	_________________ ERROR collecting tests/test_hello.py _________________
​ 	ImportError while importing test module
​ 	  '/path/to/code/ch12/script_src/tests/test_hello.py'.
​ 	​...​
​ 	tests/test_hello.py:1: in <module>
​ 	    import hello
​ 	E   ModuleNotFoundError: No module named 'hello'
​ 	======================= short test summary info ========================
​ 	ERROR tests/test_hello.py
​ 	!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!
​ 	=========================== 1 error in 0.08s ===========================
```
Our tests—and pytest—don’t know to look in ``src`` for ``hello``. All ``import`` statements, either in our source code or in our test code, use the standard Python import process; therefore, they look in directories that are found in the Python module search path. Python keeps this search path list in the ``sys.path`` [variable](https://docs.python.org/3/library/sys.html#sys.path), then pytest modifies this list a bit to add the directories of the tests it’s going to run.

What we need to do is add the directories for the source code we want to import into ``sys.path``. pytest has an option to help us with that, ``pythonpath``. The option was introduced for pytest 7. If you need to use pytest 6.2, you can use the ``pytest-srcpaths`` [plugin](https://pypi.org/project/pytest-srcpaths), to add this option to pytest 6.2.x.

First we need to modify our ``pytest.ini`` to set ``pythonpath`` to ``src``:

[ch12/script_src/pytest.ini](./script_src/pytest.ini)
```ini
​ 	​[pytest]​
​ 	addopts = ​-ra​
​ 	testpaths = ​tests​
»	pythonpath = ​src​
```
Now pytest runs just fine:
```bash
​ 	​$ ​​pytest​​ ​​tests/test_hello.py​
​ 	========================= test session starts ==========================
​ 	collected 2 items
​ 	
​ 	tests/test_hello.py ..                                           [100%]
​ 	
​ 	========================== 2 passed in 0.01s ===========================
```
That’s great that it works. But when you first encounter ``sys.path``, it can seem mysterious. Let’s take a closer look.

## Defining the Python Search Path
The Python search path is simply a list of directories Python stores in the ``sys.path`` variable. During any ``import`` statement, Python looks through the list for modules or packages matching the requested import. We can use a small test to see what ``sys.path`` looks like during a test run:

[ch12/script_src/tests/test_sys_path.py](./script_src/tests/test_sys_path.py)
```python
​ 	​import​ ​sys​
​ 	
​ 	
​ 	​def​ ​test_sys_path​():
​ 	    ​print​(​"sys.path: "​)
​ 	    ​for​ p ​in​ sys.path:
​ 	        ​print​(p)
```
When we run it, notice the search path:
```bash
​ 	​$ ​​pytest​​ ​​-s​​ ​​tests/test_sys_path.py​
​ 	========================= test session starts ==========================
​ 	collected 1 item
​ 	
​ 	tests/test_sys_path.py sys.path:
​ 	/path/to/code/ch12/script_src/tests
​ 	/path/to/code/ch12/script_src/src
​ 	​...​
​ 	/path/to/code/ch12/venv/lib/python3.10/site-packages
​ 	.
​ 	
​ 	========================== 1 passed in 0.00s ===========================
```

The last path, ``site-packages``, makes sense. That’s where packages installed via pip go. The ``script_src/tests`` path is where our test is located. The ``tests`` directory is added by pytest so that pytest can import our test module. We can utilize this addition by placing any test helper modules in the same directory as the tests using it. The ``script_src/src`` path is the path added by the ``pythonpath=src`` setting. The path is relative to the directory that contains our ``pytest.ini`` file.

## Testing requirements.txt-Based Applications
A script or application may have dependencies—other projects that need to be installed before the script or application can run. A packaged project like Cards has a list of dependencies defined in either a ``pyproject.toml``, ``setup.py``, or ``setup.cfg`` file. Cards uses ``pyproject.toml``. However, many projects don’t use packaging, and instead define dependencies in a ``requirements.txt`` file.

The dependency list in a ``requirements.txt`` file could be just a list of loose dependencies, like:

[ch12/sample_requirements.txt](./sample_requirements.txt)
```txt
​ 	typer
​ 	requests
```
However, it’s more common for applications to “pin” dependencies by defining specific versions that are known to work:

[ch12/sample_pinned_requirements.txt](./sample_pinned_requirements.txt)
```txt
​ 	typer==0.3.2
​ 	requests==2.26.0
```
The ``requirements.txt`` files are used to recreate a running environment with ``pip install -r``. The ``-r`` tells pip to read and install everything in the ``requirements.txt`` file.

A reasonable process would then be:
* Get the code somehow. For example, ``git clone <repository of project>``.
* Create a virtual environment with ``python -m venv .venv``.
* Activate the virtual environment.
* Install the dependencies with ``pip install -r requirements.txt``.
* Run the application.

For so many projects, packaging makes way more sense. However, this process is common for web frameworks like [Django](https://www.djangoproject.com) and projects using higher-level packaging, such as [Docker](https://www.docker.com). In those cases and others, ``requirements.txt`` files are common and work fine.

Let’s add a dependency to ``hello.py`` to see this situation in action. We’ll use [Typer](https://typer.tiangolo.com) to help us add a command-line argument to say hello to a certain name. First we’ll add ``typer`` to a ``requirements.txt`` file:

[ch12/app/requirements.txt](./app/requirements.txt)
```txt
​ 	typer==0.3.2
```
Notice that I also pinned the version to Typer 0.3.2. Now we can install our new dependency with either:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​typer==0.3.2​
```
or
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​-r​​ ​​requirements.txt​
```
A code change is in order as well:

[ch12/app/src/hello.py](./app/src/hello.py)
```python
​ 	​import​ ​typer​
​ 	​from​ ​typing​ ​import​ Optional
​ 	
​ 	
​ 	​def​ ​full_output​(name: str):
​ 	    ​return​ f​"Hello, {name}!"​
​ 	
​ 	
​ 	app = typer.Typer()
​ 	
​ 	
​ 	@app.command()
​ 	​def​ ​main​(name: Optional[str] = typer.Argument(​"World"​)):
​ 	    ​print​(full_output(name))
​ 	
​ 	
​ 	​if​ __name__ == ​"__main__"​:
​ 	    app()
```
Typer uses type [hints](https://docs.python.org/3/library/typing.html) to specify the type of options and arguments passed to a CLI application, including optional arguments. In the previous code we are telling Python and Typer that our application takes ``name`` as an argument, to treat it as a string, that it’s optional, and to use ``"World"`` if no ``name`` is passed in.

Just for sanity’s sake, let’s try it out:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch12/app/src​
​ 	​$ ​​python​​ ​​hello.py​
​ 	Hello, World!
​ 	​$ ​​python​​ ​​hello.py​​ ​​Brian​
​ 	Hello, Brian!
```
Cool. Now we need to modify the tests to make sure ``hello.py`` works with and without a name:

[ch12/app/tests/test_hello.py](./app/tests/test_hello.py)
```python
import hello
from typer.testing import CliRunner


def test_full_output():
    assert hello.full_output("Foo") == "Hello, Foo!"


runner = CliRunner()


def test_hello_app_no_name():
    result = runner.invoke(hello.app)
    assert result.stdout == "Hello, World!\n"


def test_hello_app_with_name():
    result = runner.invoke(hello.app, ["Brian"])
    assert result.stdout == "Hello, Brian!\n"
```
Instead of calling ``main()`` directly, we’re using Typer’s built in ``CliRunner()`` to test the app.

Let’s run it first with pytest and then with tox:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch12/app​
​ 	​$ ​​pytest​​ ​​-v​
​ 	========================= test session starts ==========================
​ 	collected 3 items
​ 	
​ 	tests/test_hello.py::test_full_output PASSED                     [ 33%]
​ 	tests/test_hello.py::test_hello_app_no_name PASSED               [ 66%]
​ 	tests/test_hello.py::test_hello_app_with_name PASSED             [100%]
​ 	
​ 	========================== 3 passed in 0.02s ===========================
```

Great. Works with pytest. Now on to tox. Because we have dependencies, we need to make sure they are installed in the tox environments. We do that by adding ``-rrequirements.txt`` to the ``deps`` setting:

[ch12/app/tox.ini](./app/tox.ini)
```ini
[tox]
envlist = py39, py310
skipsdist = true

[testenv]
deps = pytest
       pytest-srcpaths
       -rrequirements.txt
commands = pytest

[pytest]
addopts = -ra
testpaths = tests
pythonpath = src
```
That was easy. Let’s try it out:
```bash
​ 	​$ ​​tox​
​ 	py39 installed: ..., pytest==x.y,typer==x.y.z
​ 	​...​
​ 	========================= test session starts ==========================
​ 	​...​
​ 	collected 3 items
​ 	
​ 	tests/test_hello.py ...                                          [100%]
​ 	
​ 	========================== 3 passed in 0.03s ===========================
​ 	py310 ..., pytest==x.y,typer==x.y.z
​ 	​...​
​ 	========================= test session starts ==========================
​ 	​...​
​ 	collected 3 items
​ 	
​ 	tests/test_hello.py ...                                          [100%]
​ 	
​ 	========================== 3 passed in 0.02s ===========================
​ 	_______________________________ summary ________________________________
​ 	  py39: commands succeeded
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
Yay! We have an application with an external dependency listed in a ``requirements``.txt file. We are using ``pythonpath`` to specify the source code location. We added ``-rrequirements.txt`` to ``tox.ini`` to get those dependencies installed in the tox environments. And our tests run with pytest and with tox. Woohoo!

## Review
In this chapter, we looked at how to use pytest and tox to test scripts and applications. In the context of this chapter, script refers to a Python file that is run directly, as in ``python my_script.py``, and application refers to a Python script or larger application that requires dependencies to be installed with ``requirements.txt``.

In addition, you learned several techniques for testing scripts and applications:
* Using ``subprocess.run()`` and pipes to run a script and read the output
* Refactoring a script code into functions, including ``main()``
* Calling ``main()`` from a ``if __name__ == "__main__"`` block
* Using ``capsys`` to capture output
* Using ``pythonpath`` to move tests into ``tests`` and source code into src
* Specifying ``requirements.txt`` in ``tox.ini`` for applications with dependencies

## Exercises
Testing scripts can be quite fun. Running through the process on a second script will help you remember the techniques in this chapter.

The exercises start with an example script, ``sums.py``, that adds up numbers in a separate file, ``data.txt``.

Here’s ``sums.py``:

[exercises/ch12/sums.py](../exercises/ch12/sums.py)
```python
​ 	​# sums.py​
​ 	​# add the numbers in `data.txt`​
​ 	
​ 	sum = 0.0
​ 	
​ 	​with​ open(​"data.txt"​, ​"r"​) ​as​ file:
​ 	    ​for​ line ​in​ file:
​ 	        number = float(line)
​ 	        sum += number
​ 	
​ 	​print​(f​"{sum:.2f}"​)
```
And here’s an example data file:

[exercises/ch12/data.txt](../exercises/ch12/data.txt)
```txt
​ 	123.45
​ 	 76.55
```

If we run it, we should get 200.00:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/exercises/ch12​
​ 	​$ ​​python​​ ​​sums.py​​ ​​data.txt​
​ 	200.00
```

Assuming valid numbers in ``data.txt``, we need to test this script.
1. Write a test using ``subprocess.run()`` to test ``sums.py`` with ``data.txt``.
2. Modify ``sums.py`` so it can be imported by a test module.
3. Write a new test that imports ``sums`` and tests it using ``capsys``.
4. Set up tox to run your tests on at least one version of Python.
5. (Bonus) Move the tests and source into ``tests`` and ``src``. Make necessary changes to get the tests to pass.
6. (Bonus) Modify the script to pass in a file name.
   * Run the code as ``python sums.py data.txt``.
   * You should be able to use it on multiple files.
   * What different test cases would you add?
