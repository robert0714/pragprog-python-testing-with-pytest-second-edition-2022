# tox and Continuous Integration
When working with a team of people who are all working on the same codebase, continuous integration (CI) offers an amazing productivity boost. CI refers to the practice of merging all developers’ code changes into a shared repository on a regular basis—often several times a day. CI is also quite helpful even when working on a project alone.

Most tools used for CI run on a server (GitHub Actions is one example). tox is an automation tool that works a lot like a CI tool but can be run both locally and in conjunction with other CI tools on a server.

In this chapter, we take a look at tox and how to set it up in the Cards application to help us with testing Cards locally. Then we’ll set up testing on GitHub using GitHub Actions. First, let’s review what exactly CI is and how it fits into the testing universe.
## Introducing tox
[tox](https://tox.wiki/) is a command-line tool that allows you to run your complete suite of tests in multiple environments. tox is a great starting point when learning about CI. Although it strictly is not a CI system, it acts a lot like one, and can run locally. We’re going to use tox to test the Cards project in multiple versions of Python. However, tox is not limited to just Python versions. You can use it to test with different dependency configurations and different configurations for different operating systems.

In gross generalities, here’s a mental model for how tox works:

tox uses project information in either ``setup.py`` or ``pyproject.toml`` for the package under test to create an installable distribution of your package. It looks in tox.ini for a list of environments, and then for each environment, tox

1. creates a **virtual environment** in a .tox directory,
1. pip installs some dependencies,
1. builds your package,
1. pip installs your package, and
1. runs your tests.

After all environments are tested, tox reports a summary of how they all did. This makes a lot more sense when you see it in action, so let’s look at how to set up the Cards project to use tox.
> ### tox Alternatives  
>>  **💡 Tip:** Although tox is used by many projects, there are alternatives that perform similar functions. Two alternatives to tox are nox and invoke. This chapter focuses on tox mostly because it’s the tool I use.
tox-conda is a plugin that provides integration with the conda package and environment manager for the tox automation tool. It's like having your cake and eating it, too!
## Introducing tox-conda
By default, [tox](https://tox.wiki/) creates isolated environments using virtualenv and installs dependencies from pip.

In contrast, when using the [tox-conda plugin tox](https://github.com/tox-dev/tox-conda) will use conda to create environments, and will install specified dependencies from conda. This is useful for developers who rely on conda for environment management and package distribution but want to take advantage of the features provided by tox for test automation.

tox-conda has not been tested with conda version below 4.5.
### tox-conda Installation
The tox-conda package is available on pypi. To install, simply use the following command:
```bash
$ pip install tox-conda
```

## Setting Up tox
Up to now we’ve had the ``cards_proj`` code in one directory and the tests in our chapter directories. Now we’ll combine them into one project and add a ``tox.ini`` file.

Here’s the abbreviated code layout:
```bash
​ 	cards_proj
​ 	├── LICENSE
​ 	├── README.md
​ 	├── pyproject.toml
​ 	├── pytest.ini
​ 	├── src
​ 	│   └── cards
​ 	│       └── ...
​ 	├── tests
​ 	│   ├── api
​ 	│   │   └── ...
​ 	│   └── cli
​ 	│       └── ...
​ 	└── tox.ini
```
You can explore the full project at ``/path/to/code/ch11/cards_proj``. This is a typical layout for many package projects.

Let’s take a look at a basic ``tox.ini`` file in the Cards project:
[ch11/cards_proj/tox.ini](./cards_proj/tox.ini)
```ini
​ 	​[tox]​
​ 	envlist = ​py310​
​ 	isolated_build = ​True​
​ 	
​ 	​[testenv]​
​ 	deps =
​ 	  ​pytest​
​ 	  ​faker​
​ 	commands = ​pytest
```
Under ``[tox]``, we have ``envlist = py310``. This is shorthand to tell tox to run our tests using Python version 3.10. We’ll add more versions of Python shortly, but using one for now helps to understand the flow of tox. Note also the line, ``isolated_build = True``. The Cards project configures the build instructions to Python in a ``pyproject.toml`` file. For all ``pyproject.toml``-configured packages, we need to set ``isolated_build = True``. For ``setup.py``-configured projects using the setuptools library, this line can be left out.

Under ``[testenv]``, the deps section lists ``pytest`` and ``faker``. This tells tox that we need to install both of these tools for testing. You can specify which version to use, if you wish, such as ``pytest == 6.2.4`` or ``pytest >= 6.2.4``.

Finally, the ``commands`` setting tells ``tox`` to run pytest in each environment.

## Running tox
Before running tox, you have to make sure you install it:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​tox​
```

This can be done within a virtual environment.

Then to run tox, just run, well… tox:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch11/cards_proj​
​ 	​$ ​​tox​
​ 	py310 recreate: /path/to/code/ch11/cards_proj/.tox/py310
​ 	py310 installdeps: pytest, faker
​ 	py310 inst: /path/to/code/ch11/cards_proj/
​ 	           .tox/.tmp/package/1/cards-1.0.0.tar.gz
​ 	py310 installed: ...
​ 	py310 run-test: commands[0] | pytest
​ 	========================= test session starts ==========================
​ 	collected 51 items
​ 	
​ 	tests/api/test_add.py .....                                      [  9%]
​ 	tests/api/test_config.py .                                       [ 11%]
​ 	​...​
​ 	tests/cli/test_update.py .                                       [ 98%]
​ 	tests/cli/test_version.py .                                      [100%]
​ 	
​ 	========================== 51 passed in 1.32s ==========================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  congratulations :)
```

At the end, tox gives you a nice summary of all the test environments (just py310 for now) and their outcomes:
```bash
​ 	_______________________________ summary ________________________________
​ 	py310: commands succeeded
​ 	congratulations :)
```

Doesn’t that give you a nice warm, happy feeling? We got a “congratulations” and a smiley face.

## Testing Multiple Python Versions
Let’s extend envlist in tox.ini to add more Python versions:

[ch11/cards_proj/tox_multiple_pythons.ini](./cards_proj/tox_multiple_pythons.ini)
```ini
​ 	​[tox]​
​ 	envlist = ​py37, py38, py39, py310​
​ 	isolated_build = ​True​
​ 	skip_missing_interpreters = ​True​
```
Now we’ll be testing Python versions from 3.7 though 3.10.

We also added the setting, ``skip_missing_interpreters = True``. If ``skip_missing_interpreters`` is set to ``False``, the default, tox will fail if your system is missing any of the versions of Python listed. With it set to ``True``, tox will run the tests on any available Python version, but skip versions it can’t find without failing.

The output is similar. This is an abbreviated output:
```bash

​ 	​$ ​​tox​​ ​​-c​​ ​​tox_multiple_pythons.ini​
​ 	​...​
​ 	py37 run-test: commands[0] | pytest
​ 	​...​
​ 	py38 run-test: commands[0] | pytest
​ 	​...​
​ 	py39 run-test: commands[0] | pytest
​ 	​...​
​ 	py310 run-test: commands[0] | pytest
​ 	​...​
​ 	_______________________________ summary ________________________________
​ 	  py37: commands succeeded
​ 	  py38: commands succeeded
​ 	  py39: commands succeeded
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
Note that the use of an alternate configuration than ``tox.ini`` is unusual. We just used ``tox -c tox_multiple_pythons.ini`` so that we can see different ``tox.ini`` settings with the same project.

## Running tox Environments in Parallel
In the previous example, the different environments ran in a series. It’s also possible to run them in parallel with the ``-p`` flag:
```bash
​ 	​$ ​​tox​​ ​​-c​​ ​​tox_multiple_pythons.ini​​ ​​-p​
​ 	✔ OK py310 in 3.921 seconds
​ 	✔ OK py37 in 4.02 seconds
​ 	✔ OK py39 in 4.145 seconds
​ 	✔ OK py38 in 4.218 seconds
​ 	_______________________________ summary ________________________________
​ 	  py37: commands succeeded
​ 	  py38: commands succeeded
​ 	  py39: commands succeeded
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
Note that the output is not abbreviated. This is actually all the output you see if everything passes.

## Adding a Coverage Report to tox
With a couple of changes to the ``tox.ini`` file, tox can add coverage reports to its test runs. To do so, we need to add ``pytest-cov`` to the deps setting so that the ``pytest-cov`` plugin will be installed in the tox test environments. Pulling in ``pytest-cov`` will also include all of its dependencies, like ``coverage``. We then extend the ``commands`` call to ``pytest`` to be ``pytest --cov=cards``:

[ch11/cards_proj/tox_coverage.ini](./cards_proj/tox_coverage.ini)
```ini
​ 	​[testenv]​
​ 	deps =
​ 	  ​pytest​
​ 	  ​faker​
​ 	  ​pytest-cov​
​ 	commands = ​pytest --cov=cards​
```
When using ``coverage`` with tox, it’s also nice to set up a ``.coveragerc`` file to let ``coverage`` know which source paths should be considered identical:

[ch11/cards_proj/.coveragerc](./cards_proj/.coveragerc)
```ini
​ 	[paths]
​ 	source =
​ 	   src
​ 	   .tox/*/site-packages
```

This looks a little cryptic at first. tox creates virtual environments in the ``.tox`` directory (for example, in ``.tox/py310``). The Cards source is in the ``src/cards`` directory before we run. But when tox installs our package into the environment, it will live in a ``site-packages/cards`` directory somewhere buried in ``.tox``. For example, for Python 3.10, it shows up in ``.tox/py310/lib/python3.10/site-packages/cards``.

The coverage ``source`` setting to the list including ``src`` and ``.tox/*/site-packages`` is shorthand to make the earlier code work such that the following output is possible:
```bash
​ 	​$ ​​tox​​ ​​-c​​ ​​tox_coverage.ini​​ ​​-e​​ ​​py310​
​ 	​...​
​ 	py310 run-test: commands[0] | pytest --cov=cards
​ 	​...​
​ 	---------- coverage: platform darwin, python 3.x.y -----------
​ 	Name                    Stmts   Miss  Cover
​ 	-------------------------------------------
​ 	src/cards/__init__.py       3      0   100%
​ 	src/cards/api.py           72      0   100%
​ 	src/cards/cli.py           86      0   100%
​ 	src/cards/db.py            23      0   100%
​ 	-------------------------------------------
​ 	TOTAL                     184      0   100%
​ 	
​ 	
​ 	========================== 51 passed in 0.44s ==========================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  congratulations :)
```

In this example, note that we also used the ``-e py310`` flag to choose a specific environment.

## Specifying a Minimum Coverage Level
When running ``coverage`` from tox, it’s also nice to set a baseline coverage percent to flag any slips in coverage. This is done with the ``--cov-fail-under`` flag:

[ch11/cards_proj/tox_coverage_min.ini](./cards_proj/tox_coverage_min.ini)
```ini
​ 	​[testenv]​
​ 	deps =
​ 	  ​pytest​
​ 	  ​faker​
​ 	  ​pytest-cov​
​ 	commands = ​pytest --cov=cards --cov=tests --cov-fail-under=100​
```
This will add an extra line to the output:
```bash
​ 	​$ ​​tox​​ ​​-c​​ ​​tox_coverage_min.ini​​ ​​-e​​ ​​py310​
​ 	​...​
​ 	Name                        Stmts   Miss  Cover
​ 	-----------------------------------------------
​ 	src/cards/__init__.py           3      0   100%
​ 	src/cards/api.py               72      0   100%
​ 	src/cards/cli.py               86      0   100%
​ 	​...​
​ 	tests/cli/test_version.py       3      0   100%
​ 	tests/conftest.py              22      0   100%
​ 	-----------------------------------------------
​ 	TOTAL                         439      0   100%
​ 	
»	Required test coverage of 100% reached. Total coverage: 100.00%
​ 	
​ 	========================== 51 passed in 0.43s ==========================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  congratulations :)
```
We used a couple of other flags as well. In ``tox.ini``, we added ``--cov=tests`` to the pytest call to make sure all of our tests are run. In the tox command line, we used ``-e py310``. The ``-e`` flag allows us to run one specific tox environment.

## Passing pytest Parameters Through tox
In the previous section we saw how using ``-e py310`` enables us to zoom in on one environment to run. We could also zoom in on an individual test if we make one more modification to allow parameters to get to pytest.

The changes are as simple as adding ``{posargs}`` to our pytest command:

[ch11/cards_proj/tox_posargs.ini](./cards_proj/tox_posargs.ini)
```ini
​ 	​[testenv]​
​ 	deps =
​ 	  ​pytest​
​ 	  ​faker​
​ 	  ​pytest-cov​
​ 	commands =
​ 	  ​pytest​ --cov=​cards --cov=tests --cov-fail-under=100 {posargs}​
```
Then to pass arguments to pytest, add a ``--`` between the tox arguments and the pytest arguments. In this case, we’ll select ``test_version`` tests using keyword flag ``-k``. We’ll also use ``--no-cov`` to turn off ``coverage`` (no point in measuring coverage when we’re only running a couple of tests):
```bash
​ 	​$ ​​tox​​ ​​-c​​ ​​tox_posargs.ini​​ ​​-e​​ ​​py310​​ ​​--​​ ​​-k​​ ​​test_version​​ ​​--no-cov​
​ 	​...​
​ 	py310 run-test: commands[0] | pytest --cov=cards --cov=tests
​ 	 --cov-fail-under=100 -k test_version --no-cov
​ 	========================= test session starts ==========================
​ 	collected 51 items / 49 deselected / 2 selected
​ 	
​ 	tests/api/test_version.py .                                      [ 50%]
​ 	tests/cli/test_version.py .                                      [100%]
​ 	
​ 	=================== 2 passed, 49 deselected in 0.10s ===================
​ 	_______________________________ summary ________________________________
​ 	  py310: commands succeeded
​ 	  congratulations :)
```

tox is capable of doing many other cool things. Check the [tox](https://tox.wiki/) documentationfor specific needs not covered here.

tox is not only awesome for automating testing processes locally, but also it helps with cloud-based CI. Let’s move on to running pytest and tox using GitHub Actions.

## Running tox with GitHub Actions
Even if you are careful to run tox all the time before committing or merging your code, it’s really nice to have a CI system set up to always run tox on all changes. Even though GitHub Actions has only been available since 2019, it’s already very popular for Python projects.

[GitHub Actions](https://github.com/features/actions) is a cloud-based CI system provided by GitHub. If you are using GitHub to store your project, Actions are a natural CI option.

> ### CI Alternatives 
>>  **💡 Tip:** GitHub Actions is just one example of a continuous integration tool. There are many other great tools available, such as GitLab CI, Bitbucket Pipelines, CircleCI, and Jenkins.

To add Actions to a repository, all you have to do is add a workflow``.yml`` file to ``.github/workflows/`` at the top level of your project.

Let’s look at ``main.yml`` for Cards:
[ch11/cards_proj/.github/workflows/main.yml](./cards_proj/.github/workflows/main.yml)
```yml
name: CI

on: [push, pull_request]

jobs:
  build:

    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.7", "3.8", "3.9", "3.10"]

    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python }}
      - name: Install Tox and any other packages
        run: pip install tox
      - name: Run Tox
        run: tox -e py
```
Now let’s walk through what this file is specifying:
* ``name`` can be anything. It shows up in the GitHub Actions user interface that we’ll see in a bit.
* ``on: [push, pull_request]`` tells Actions to run our tests every time we either push code to the repository or a pull request is created. If we push code changes, our tests will run. If anyone creates a pull request, the tests will run. On pull requests, the result of the test run can be seen in the pull request interface. All action run results can be seen in the Actions tab on the GitHub interface. We’ll see that shortly.
* ``runs-on: ubuntu-latest`` specifies which operating system to run the tests on. Here we’re just running on Linux, but other OSs are available.
* ``matrix: python: ["3.7", "3.8", "3.9", "3.10"]`` specifies which Python version to run.
* ``steps`` is a list of steps. The ``name`` of each step can be anything and is optional.
* ``uses: actions/checkout@v2`` is a GitHub Actions tool that checks out our repository so the rest of the workflow can access it.
* ``uses: actions/setup-python@v2`` is a GitHub Actions tool that gets Python configured and installed in a build environment.
* ``with: python-version: ${{ matrix.python }}`` says to create an environment for each of the Python versions listed in ``matrix: python``.
* ``run: pip install tox`` installs tox.
* ``run: tox -e py`` runs tox. The ``-e py`` is a bit surprising because we don’t have a ``py`` environment specified. However, this works to select the correct version of Python specified in our ``tox.ini``.

The Actions syntax can seem mysterious at first. Luckily it’s documented well. A good starting point in the GitHub Actions documentation is the Building and [Testing Python page](
https://docs.github.com/en/actions/guides/building-and-testing-python). The documentation also shows you how to run pytest directly without tox and how to extend the matrix to multiple operating systems.

Once you’ve set up your workflow``.yml`` file and pushed it to your GitHub repository, it will be run automatically.

Notice how our top-level name setting, “Python package,” shows up at the top, and the names for each step are shown as well.

> ### Running Other Tools from tox and CI
>>  **💡 Tip:** We used tox and GitHub Actions to run pytest. However, these tools can do so much more. Many projects use these tools to run other tools for static analysis, type checking, code format checks, and so on. Please visit the documentation for both tox and GitHub Actions to find out more.
## Review
In this chapter, we set up both tox and GitHub Actions to run pytest on multiple Python versions. You also saw how to
* run tox environments in parallel,
* test with ``coverage``,
* set a minimum coverage percentage,
* run specific environments,
* pass parameters from the tox command line to pytest, and
* run tox on GitHub Actions.

## Exercises
Working with tox is even more fun than reading about it. Running through these exercises will help you realize how simple it is to work with tox. A small starter project with a starter ``tox.ini`` set to run tests using Python 3.10 is in the ``/path/to/code/exercises/ch11`` folder. Use that project to complete the following exercises.
1. Go to ``/path/to/code/exercises/ch11``. Install tox.
2. Run tox with the current settings.
3. Change ``envlist`` to also run Python 3.9.
4. Change commands to add coverage report, including making sure there is 100% coverage. Don’t forget to add ``pytest-cov`` to ``deps``.
5. Add ``{posargs}`` to the end of the pytest command. Run ``tox -e py310 -- -v`` to see the test names.
6. (Bonus) Set up GitHub Actions to run tox for this project, or some other Python project repository.