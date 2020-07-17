# pyvue
<p align="center">

<a href="https://pypi.python.org/pypi/pyvuejs">
<img src="https://img.shields.io/pypi/v/pyvuejs.svg" /></a>
<a href="https://travis-ci.org/eseunghwan/pyvuejs"><img src="https://travis-ci.org/eseunghwan/pyvuejs.svg?branch=master" /></a>
</p>
Pythonic Vue.js MPA Toolkit

<br>
<br>
<br>
<br>

# Install
## using pip
```powershell
pip install pyvuejs
```
## from git
```powershell
git clone https://github.com/eseunghwan/pyvuejs.git
cd pyvuejs
python setup.py install
```

<br>
<br>

# Usage
## create project with cli
```powershell
python -m pyvuejs init

[output]
//=========== pyvuejs project init ===========//
AppName: 
```
<br>

## move to project directory and start with cli
### default host = 0.0.0.0, port = 8000
```powershell
python -m pyvuejs start

[output]
//=========== start pyvuejs app ===========//
Running on http://0.0.0.0:8000 (CTRL + C to quit)
[2020-07-17 18:46:40,927] Running on 0.0.0.0:8000 over http (CTRL + C to quit)
```
<br>

## start command line options
- ### host only
```powershell
python -m pyvuejs start 127.0.0.1
```

- ### port only
```powershell
python -m pyvuejs start 9000
```

- ### both host and port
```powershell
python -m pyvuejs start 127.0.0.1 9000
```

<br>
<br>

# PVUE editing guide
### pvue file is a single view file against with vue file
### pvue needs 4 code blocks
<br>

## template(<b>required</b>)
### template block is shown part of pvue
### code style is absolutely same as <b>Vue.js</b>
```html
<template>
    <div id="app1">
        <!-- elements -->
    </div>
</template>
```

## model(<b>required</b>)
### model block is server-side part of pvue
### code style is <i>python</i>, it's sensitive to <b>tabs</b>
```python
<model>
Model app1:
    # variables
    testVar = 10

    # compute methods
    def compute_testVar(self):
        self.testVar -= 1
</model>
```

## style(<i>optional</i>)
### style block is style part of template block
```html
<style>
div#app1 {
    /* styles */
}
</style>
```

## script(<i>optional</i>)
### script block runs in page
### custom events, attributes can be set in script block
```html
<script>
    /* scripts */
</script>
```

<br>
<br>

# License
### pyvuejs is MIT license

<br>
<br>

# Credits
This package was created with Cookiecutter and the `cs01/cookiecutter-pypackage` project template.

[Cookiecutter](https://github.com/audreyr/cookiecutter)

[cs01/cookiecutter-pypackage](https://github.com/cs01/cookiecutter-pypackage)
