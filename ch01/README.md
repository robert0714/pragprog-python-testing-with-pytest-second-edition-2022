# Getting Started with pytest
## Setting ENvironment

## In Linux    
```bash  
​ 	$ python3 -m venv venv
​ 	$ source venv/bin/activate
​ 	(venv) $ pip install pytest
```
## In Windows
### CMD
```cmd 
   C:\> python -m venv venv
   C:\> venv\Scripts\activate.bat
   C:\> pip install pytest
```
### Powershell
```powershell 
​ 	PS C:\> python -m venv venv
​ 	PS C:\> venv\Scripts\Activate.ps1
​ 	PS C:\> pip install pytest
```
## In basic python
```
pip install pytest pylint 
```
## In AnaConda
Installing `pytest` from the `conda-forge` channel can be achieved by adding `conda-forge` to your channels with:

```
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Once the `conda-forge` channel has been enabled, `pytest` can be installed with `conda`:

```
conda install pytest pylint -c conda-forge --yes
```

or with `mamba`:

```
mamba install pytest
```

It is possible to list all of the versions of `pytest` available on your platform with `conda`:

```
conda search pytest --channel conda-forge
```

or with `mamba`:

```
mamba search pytest --channel conda-forge
```

Alternatively, `mamba repoquery` may provide more information:

```
# Search all versions available on your platform:
mamba repoquery search pytest --channel conda-forge

# List packages depending on `pytest`:
mamba repoquery whoneeds pytest --channel conda-forge

# List dependencies of `pytest`:
mamba repoquery depends pytest --channel conda-forge
```
## Running pytest
With pytest installed, we can run test_passing(). This is what it looks like when it’s run:
```bash
​​pytest​​ ​​test_one.py
```
 If you need more information, you can use **-v** or **--verbose**:
```bash
​​pytest​ ​​-v​​ ​​ ​​test_one.py
``` 
That’s already a lot of information, but there’s a line that says **Use -v to get the full diff**. Let’s do that:
```bash
​​​pytest​​ ​​-v​​ ​​test_two.py
``` 
It looks for .py files starting with **test_** or ending with **_test**. From the ch1 directory, if you run pytest **with no commands**, you’ll run two files’ worth of tests:
```bash
​​pytest​​ ​​--tb=no
``` 
I also used the **--tb=no** flag to turn off tracebacks, since we don’t really need the full output right now. We’ll be using various flags throughout the book.

We can also specify a test function within a test file to run by adding **::test_name** to the file name:
```bash
pytest​​ ​​-v​​ ​​ch1/test_one.py::test_passing
```
### Test Discovery
The part of pytest execution where pytest goes off and finds which tests to run is called **test discovery**. pytest was able to find all the tests we wanted it to run because we named them according to the pytest naming conventions.

Given no arguments, pytest looks at your current directory and all subdirectories for test files and runs the test code it finds. If you give pytest a filename, a directory name, or a list of those, it looks there instead of the current directory. Each directory listed on the command line is examined for test code, as well as any subdirectories.

Here’s a brief overview of the naming conventions to keep your test code discoverable by pytest:
* Test files should be named **test_<something>.py** or **<something>_test.py**.
* Test methods and functions should be named **test_<something>**.
* Test classes should be named **Test<Something>**.

Because our test files and functions start with **test_**, we’re good. There are ways to alter these discovery rules if you have a bunch of tests named differently. I’ll cover how to do that in **Chapter 8, ​Configuration Files**​.
### Test Outcomes
So far we’ve seen one passing test and one failing test. However, pass and fail are not the only outcomes possible.

Here are the possible outcomes of a test:
* PASSED (.)—The test ran successfully.
* FAILED (F)—The test did not run successfully.
* SKIPPED (s)—The test was skipped. You can tell pytest to skip a test by using either the **@pytest.mark.skip()** or **@pytest.mark.skipif()** decorators, which are discussed in ​Skipping Tests with pytest.mark.skip​.
* XFAIL (x)—The test was not supposed to pass, and it ran and failed. You can tell pytest that a test is expected to fail by using the **@pytest.mark.xfail()** decorator, which is discussed in ​Expecting Tests to Fail with pytest.mark.xfail​.
* XPASS (X)—The test was marked with xfail, but it ran and passed.
* ERROR (E)—An exception happened either during the execution of a fixture or hook function, and not during the execution of a test function. Fixtures are discussed in Chapter 3, ​pytest Fixtures​, and hook functions are discussed in Chapter 15, ​Building Plugins​.