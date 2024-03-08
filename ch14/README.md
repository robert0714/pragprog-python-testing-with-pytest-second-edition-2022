# Chapter 14 Third-Party Plugins
As powerful as pytest is right out of the box, it gets even better when we add plugins to the mix. The pytest code base is designed to allow customization and extensions, and there are hooks available to allow modifications and improvements through plugins.

It might surprise you to know that you’ve already written some plugins if you’ve worked through the previous chapters in this book. Any time you put fixtures and/or hook functions into a project’s ``conftest.py`` file, you create a local plugin. It’s just a little bit of extra work to convert these ``conftest.py`` files into installable plugins that you can share between projects, with other people, or with the world.

We’ll start this chapter by looking at where to find third-party plugins. Quite a few plugins are available, so there’s a decent chance someone has already written the change you want to make to pytest. We’ll take a look at a handful of plugins that are broadly useful to many software projects. Finally, we’ll explore the variety available by taking a quick tour of many types of plugins.
## Finding Plugins
You can find third-party pytest plugins in several places.
* https://docs.pytest.org/en/latest/reference/plugin_list.html    
  The main pytest documentation site includes an alphabetized list of plugins pulled from pypi.org. It’s a big list.
* https://pypi.org   
  The Python Package Index (PyPI) is a great place to get lots of Python packages, but it is also a great place to find pytest plugins. When looking for pytest plugins, it should work pretty well to search for **pytest**, ``pytest-`` or ``-pytest``, as most pytest plugins either start with ``pytest-`` or end in ``-pytest``. You can also filter by classifier ``"Framework::Pytest"``, which will include packages that include a pytest plugin but aren’t named pytest- or ``-pytest``, such as Hypothesis and Faker.
* https://github.com/pytest-dev   
  The ``pytest-dev`` group on GitHub is where the pytest source code is kept. It’s also where you can find many popular pytest plugins. For plugins, the ``pytest-dev`` group is intended as a central location for popular pytest plugins and to share some of the maintenance responsibility. Refer to “Submitting Plugins to pytest-dev” on [the docs.pytest.org website](https://docs.pytest.org/en/latest/contributing.html#submitting-plugins-to-pytest-dev) for more information.
* https://docs.pytest.org/en/latest/how-to/plugins.html   
  The main pytest documentation site has a page that talks about installing and using pytest plugins, and lists a few common plugins.

Let’s look at the various ways you can install plugins with ``pip install``.

## Installing Plugins
pytest plugins are installed with pip, just like the other Python packages you’ve already installed in the earlier chapters in this book.

For example:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​pytest-cov​
```
This installs the latest stable version from PyPI. However, pip is quite powerful and can install packages from other places like local directories and Git repositories. See Appendix 2, ​pip​ for more information.
## Exploring the Diversity of pytest Plugins
The Plugin List from [the main pytest documentation site](https://docs.pytest.org/en/latest/reference/plugin_list.html)  lists almost 1000 plugins last time I checked. That’s a lot of plugins. Let’s take a look at a small subset of plugins that are both useful to lots of people and show the diversity of what we can do with plugins.

All of the following plugins are available via PyPI.

### Plugins That Change the Normal Test Run Flow
pytest, by default, runs our tests in a predictable flow. Given a single directory of test files, pytest will run each file in alphabetical order. Within each file, each test is run in the order it appears in the file.

Sometimes it’s nice to change that order. The following plugins in some way change the normal test run flow:
* ``pytest-order``—Allows us to specify the order using a marker
* ``pytest-randomly``—Randomizes the order, first by file, then by class, then by test
* ``pytest-repeat``—Makes it easy to repeat a single test, or multiple tests, a specific number of times
* ``pytest-rerunfailures``—Re-runs failed tests. Helpful for flaky tests
* ``pytest-xdist``—Runs tests in parallel, either using multiple CPUs on one machine, or multiple remote machines

### Plugins That Alter or Enhance Output
The normal pytest output shows mostly dots for passing tests, and characters for other output. Then you’ll see lists of test names with outcome if you pass in ``-v``. However, there are plugins that change the output.
* ``pytest-instafail``—Adds an ``--instafail`` flag that reports tracebacks and output from failed tests right after the failure. Normally, pytest reports tracebacks and output from failed tests after all tests have completed.
* ``pytest-sugar``—Shows green checkmarks instead of dots for passing tests and has a nice progress bar. It also shows failures instantly, like ``pytest-instafail``.
* ``pytest-html``—Allows for html report generation. Reports can be extended with extra data and images, such as screenshots of failure cases.

### Plugins for Web Development
pytest is used extensively for testing web projects, so it’s no surprise there’s a long list of plugins to help with web testing.
* ``pytest-selenium``—Provides fixtures to allow for easy configuration of browser-based tests. Selenium is a popular tool for browser testing.
* ``pytest-splinter``—Built on top of Selenium as a higher level interface, this allows Splinter to be used more easily from pytest.
* ``pytest-django`` and ``pytest-flask``—Help make testing Django and Flask applications easier with pytest. Django and Flask are two of the most popular web frameworks for Python.

### Plugins for Fake Data
We used Faker in [​Combining Markers with Fixtures](../ch06/README.md)​ to generate card summary and owner data. There are many cases in different domains where it’s helpful to have generated fake data. Not surprisingly, there are several plugins to fill that need.
* ``Faker``—Generates fake data for you. Provides ``faker`` fixture for use with pytest
* ``model-bakery``—Generates Django model objects with fake data.
* ``pytest-factoryboy``—Includes fixtures for Factory Boy, a database model data generator
* ``pytest-mimesis``—Generates fake data similar to Faker, but Mimesis is quite a bit faster

### Plugins That Extend pytest Functionality
All plugins extend pytest functionality, but I was running out of good category names. This is a grab bag of various cool plugins.
* ``pytest-cov``—Runs coverage while testing
* ``pytest-benchmark``—Runs benchmark timing on code within tests
* ``pytest-timeout``—Doesn’t let tests run too long
* ``pytest-asyncio``—Tests async functions
* ``pytest-bdd``—Writes behavior-driven development (BDD)–style tests with pytest
* ``pytest-freezegun``—Freezes time so that any code that reads the time will get the same value during a test. You can also set a particular date or time.
* ``pytest-mock``—A thin-wrapper around the unittest.mock patching API

While many may find the plugins listed in this section helpful, two plugins in particular find near universal approval in helping to speed up testing and finding accidental dependencies between tests: ``pytest-xdist`` and ``pytest-randomly``. Let’s take a closer look at those next.
## Running Tests in Parallel
Usually all tests run sequentially. And that’s just what you want if your tests hit a resource that can only be accessed by one client at a time. However, if your tests do not need to access a shared resource, you could speed up test sessions by running multiple tests in parallel. The pytest-xdist plugin allows you to do that. You can specify multiple processors and run many tests in parallel. You can even push off tests onto other machines and use more than one computer.

For example, let’s look at the following simple test:

[ch14/test_parallel.py](./test_parallel.py)
```python
​ 	​import​ ​time​
​ 	
​ 	
​ 	​def​ ​test_something​():
​ 	    time.sleep(1)
```
Running it takes about one second:
```bash
​ 	​$ ​​cd​​ ​​/path/to/code/ch14​
​ 	​$ ​​pytest​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	collected 1 item
​ 	
​ 	test_parallel.py .                                               [100%]
​ 	
​ 	========================== 1 passed in 1.01s ===========================
```
If we use ``pytest-repeat`` to run it 10 times with ``--count=10``, it should take about 10 seconds:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​pytest-repeat​
​ 	​$ ​​pytest​​ ​​--count=10​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	collected 10 items
​ 	
​ 	test_parallel.py ..........                                      [100%]
​ 	
​ 	========================= 10 passed in 10.05s ==========================
```
Now we can speed things up by running those tests in parallel on four CPUs with ``-n=4``:
```bash

​ 	​$ ​​pip​​ ​​install​​ ​​pytest-xdist​
​ 	​$ ​​pytest​​ ​​--count=10​​ ​​-n=4​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	gw0 [10] / gw1 [10] / gw2 [10] / gw3 [10]
​ 	..........                                                       [100%]
​ 	========================== 10 passed in 3.49s ==========================
```
We can use ``-n=auto`` to run on as many CPU cores as possible:
```bash
​ 	​$ ​​pytest​​ ​​--count=10​​ ​​-n=auto​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	gw0 I / gw1 I / gw2 I ...
​ 	..........                                                       [100%]
​ 	========================== 10 passed in 2.16s ==========================
```
This was running on a six-core processor. So it seems like maybe we should be able to run it six times on six cores and get it down to about one second again:
```bash
​ 	​$ ​​pytest​​ ​​--count=6​​ ​​-n=6​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	gw0 [6] / gw1 [6] / gw2 [6] / gw3 [6] / gw4 [6] / gw5 [6]
​ 	......                                                           [100%]
​ 	========================== 6 passed in 1.63s ===========================
```
Not quite. 1.63 seconds. There is some overhead involved with spawning parallel processes and combining results in the end. However, the overhead is fairly constant, so for large jobs, it’s worth it.

Here’s the same ``-n=6`` for 60 tests:
```bash
​ 	​$ ​​pytest​​ ​​--count=60​​ ​​-n=6​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	gw0 [60] / gw1 [60] / gw2 [60] / gw3 [60] / gw4 [60] / gw5 [60]
​ 	............................................................     [100%]
​ 	========================= 60 passed in 10.71s ==========================
```
The overhead just grew a little with 10 times the tests, from 0.63 seconds to 0.71 seconds.

I’ve noted in these examples ``-n=6``. However, it is a better practice to run on ``-n=auto`` to get the best speedup. I honestly don’t know how this works as well as it does, but even though I have six cores, ``-n=auto`` is faster than ``-n=6``:
```bash
​ 	​$ ​​pytest​​ ​​--count=60​​ ​​-n=auto​​ ​​test_parallel.py​
​ 	========================= test session starts ==========================
​ 	gw0 I / gw1 I / gw2 I ...
​ 	............................................................     [100%]
​ 	========================== 60 passed in 6.14s ==========================
```
That’s a little over six seconds for 60 seconds of test work.

The ``pytest-xdist`` plugin has another nice feature bundled with it: the ``--looponfail`` flag. The ``--looponfail`` flag enables you to run tests repeatedly in a subprocess. After each run, pytest waits until a file in your project changes and then re-runs the previously failing tests. This is repeated until all tests pass after which again a full run is performed. This feature is pretty cool for debugging a bunch of test failures.
## Randomizing Test Order
Generally we’d like each of our tests to be able to run independently of all other tests. Having independent tests allows for easy debugging if something ever fails. If test order inadvertently depends on the state of the system being tested, that independence is broken. One common way to test for order independence is to randomize the test run order.

The ``pytest-randomly`` plugin is excellent randomizing test order. It also randomizes the seed value for other random tools like Faker and Factory Boy. Let’s try it out on a couple simple test files:

[ch14/random/test_a.py](./random/test_a.py)
```python
​ 	​def​ ​test_one​():
​ 	    ​pass​
​ 	
​ 	
​ 	​def​ ​test_two​():
​ 	    ​pass​
```
[ch14/random/test_b.py](./random/test_b.py)
```python
​ 	​def​ ​test_three​():
​ 	    ​pass​
​ 	
​ 	
​ 	​def​ ​test_four​():
​ 	    ​pass
```

If we run these normally, we get tests one through four:
```bash
​ 	​$ ​​cd​​ ​​path/to/code/ch14/random​
​ 	​$ ​​pytest​​ ​​-v​
​ 	========================= test session starts ==========================
​ 	collected 4 items
​ 	
​ 	test_a.py::test_one PASSED                                       [ 25%]
​ 	test_a.py::test_two PASSED                                       [ 50%]
​ 	test_b.py::test_three PASSED                                     [ 75%]
​ 	test_b.py::test_four PASSED                                      [100%]
​ 	
​ 	========================== 4 passed in 0.01s ===========================
```
``test_a.py`` runs before ``test_b.py`` due to alphabetical order. Then the tests within the files run in the order they appear in the file.

To randomize the order, install ``pytest-randomly``:
```bash
​ 	​$ ​​pip​​ ​​install​​ ​​pytest-randomly​
​ 	​$ ​​pytest​​ ​​-v​
​ 	========================= test session starts ==========================
​ 	collected 4 items
​ 	
​ 	test_b.py::test_four PASSED                                      [ 25%]
​ 	test_b.py::test_three PASSED                                     [ 50%]
​ 	test_a.py::test_two PASSED                                       [ 75%]
​ 	test_a.py::test_one PASSED                                       [100%]
​ 	
​ 	========================== 4 passed in 0.01s ===========================
```
Making sure your tests run fine in random order may seem like a weird thing to care about. However, tests that aren’t properly isolated have caused many a late-night debugging session. Randomizing your tests on a regular basis can help you avoid these problems.

## Review
In this chapter, we looked at where to find plugins:
* https://pypi.org (search for pytest-)
* https://github.com/pytest-dev
* https://docs.pytest.org/en/latest/how-to/plugins.html
* https://docs.pytest.org/en/latest/reference/plugin_list.html

We quickly looked at the variety of plugins available, and specifically tried out using ``pytest-randomly``, ``pytest-repeat``, and ``pytest-xdist``.

## Exercises
pytest is incredibly powerful by itself. However, it’s important to understand the range and power achievable with the additions of plugins. Taking a moment to explore the resources available and trying a few plugins really will help you to remember where to look when you actually need help on a real testing project.
1. Head over to ``pypy.python.org`` with your favorite browser. Search for ``pytest-``.
    * How many projects are listed?
2. Activate the virtual environment you were using in Chapter 13.
    * Run the full test suite.
    * How long does it take?
3. Install ``pytest-xdist``.
    * Re-run the tests with ``--n=auto``.
    * What was the time for the test suite?