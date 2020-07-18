<h1 style="font-size:50px;">pyvuejs</h1>
<p align="center">

<a href="https://pypi.python.org/pypi/pyvuejs">
<img src="https://img.shields.io/pypi/v/pyvuejs.svg" /></a>
<a href="https://travis-ci.org/eseunghwan/pyvuejs"><img src="https://travis-ci.org/eseunghwan/pyvuejs.svg?branch=master" /></a>
</p>

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
- ### default host = "0.0.0.0", port = 8000
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
- ### pvue file is a single view file against with vue file
<br>

## prefix(<i>optional</i>, default = "view")
- ### prefix defines pvue is view or component
```html
<!-- if pvue is view -->
!prefix view
<!-- if pvue is component -->
!prefix component
<!-- if blank, consider as view -->
```
<br>

## template(<b>required</b>)
- ### template block is shown part of pvue
- ### code style is very same as <b>Vue.js</b>
```html
<template>
    <div id="app1">
        <!-- elements -->
        <p>{{ testVar }}</p>
        <button>[buttonText]</button>

        <!-- if show components -->
        <component name="[componentName]">
    </div>
</template>
```
<br>

## model(<b>required</b>)
- ### model block is server-side part of pvue
- ### code style is <i>python</i>, it's sensitive to <b>tabs</b>
```python
<model>
Model app1:
    # variables
    testVar = 10

    # compute methods
    @testVar.connect("method")
    # to use session, add "session" argument to function
    def sub_testVar(self, session):
        self.testVar -= 1
</model>
```
- ### connect to vue properties
    - currently, <b>computed</b> and <b>method</b> are enable
    - add decorator on top of function
    ```python
    @sample.connect("method")
    def get_sample(self):
        self.sample = "It's sample!"
    ```
<br>

## style(<i>optional</i>)
- ### style block is style part of template block
```html
<style>
div#app1 {
    /* styles */
}
</style>
```
<br>

## script(<i>optional</i>)
- ### script block runs in page
- ### custom events, attributes can be set in script block
```html
<script>
    /* scripts */
</script>
```

<br>
<br>

# Todo
- ### [x] enable componenting(V 0.2.0)
- ### [x] multi locational data binding(V 0.2.0)
- ### [x] dataSession (V 0.2.0)
- ### add vue properties
    - [x] method (V 0.1.0)
    - [x] computed (V 0.2.0)
    - [ ] watch

<br>
<br>

# License
### pyvuejs is MIT license

<br>
<br>

# Release History
* ### V 0.1.0 [2020/07/17]
    - initial commit

* ### V 0.2.0 [2020/07/18]
    - enable componenting
    - multi locational data binding
    - add <b>computed</b> binding
    - dataSession
