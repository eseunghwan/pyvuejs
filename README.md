# pyvuejs
<p align="center">

<a href="https://pypi.python.org/pypi/pyvuejs">
<img src="https://img.shields.io/pypi/v/pyvuejs.svg" /></a>
<a href="https://travis-ci.org/eseunghwan/pyvuejs"><img src="https://travis-ci.org/eseunghwan/pyvuejs.svg?branch=master" /></a>
</p>

<br>
<br>

# Install
### using pip
```powershell
pip install pyvuejs
```
### from git
```powershell
git clone https://github.com/eseunghwan/pyvuejs.git
cd pyvuejs
python setup.py install
```

<br>
<br>

# Usage
### create project with cli
```powershell
python -m pyvuejs init

[output]
//=========== pyvuejs project init ===========//
AppName: 
```
<br>

### move to project directory and start with cli
- default host = "0.0.0.0", port = 8000
```powershell
python -m pyvuejs start

[output]
//=========== start pyvuejs app ===========//
Running on http://0.0.0.0:8000 (CTRL + C to quit)
[2020-07-17 18:46:40,927] Running on 0.0.0.0:8000 over http (CTRL + C to quit)
```
<br>

### start command line options
- host only
```powershell
python -m pyvuejs start 127.0.0.1
```

- port only
```powershell
python -m pyvuejs start 9000
```

- both host and port
```powershell
python -m pyvuejs start 127.0.0.1 9000
```

<br>
<br>

# PVUE editing guide
pvue file is a single view file against with vue file
<br>

### prefix(<i>optional</i>, default = "view")
- prefix defines pvue is view or component
```html
<!-- if pvue is view -->
!prefix view
<!-- if pvue is component -->
!prefix component
<!-- if blank, consider as view -->
```
<br>

### template(<b>required</b>)
- template block is shown part of pvue
- code style is very same as <b>Vue.js</b>
```html
<template>
    <div id="app1">
        <!-- elements -->
        <p>{{ testVar }}</p>
        <!-- to use session values -->
        <p>{{ session.sharedVar }}</p>
        <button>click me!</button>

        <!-- if show components -->
        <component name="[componentName]" />
    </div>
</template>
```
<br>

### model(<b>required</b>)
- model block is server-side part of pvue
- code style is <i>python</i>, it's sensitive to <b>tabs</b>
```python
<model>
Model app1:
    # variables
    testVar = 10
    # to upload variable too session
    sharedVar:session = 30

    # event bind
    @event("load")
    def onApp1Load(self, session):
        self.testVar = 20
        # invoke to session variable
        session["sharedVar"] = 50

    # compute methods
    @method
    # to use session, add "session" argument to function
    def sub_testVar(self, session):
        # can import custom modules from app directory
        from plugins import *

        # can compute variables
        self.testVar -= 1

        # defined by ":session", use it without define to session in code
        print(session["sharedVar"])
</model>
```
- connect to vue properties
    - currently, <b>computed</b> and <b>method</b> are able
    - add decorator on top of function
    ```python
    @method
    def get_sample(self):
        self.sample = "It's sample!"
    ```
- bind to events
    - currently, <b>load</b> and <b>show</b> are able
    - add event decorator on top of function
    ```python
    @event("load")
    def load_sample(self):
        print("onload!")

    @event("show")
    def show_sample(self):
        print("onshow!")
    ```
<br>

### resource(<i>optional</i>)
- resource block loads app's static files
- app's static url is <b>"/app"</b>
```html
<resource>
    <!-- css -->
    <link rel="stylesheet" href="/app/[staticFileName]">
    <!-- js -->
    <script type="text/javascript" src="/app/[staticFileName]"></script>
</resource>
```
<br>

### style(<i>optional</i>)
- style block is style part of template block
```html
<style>
div#app1 {
    /* styles */
}
</style>
```
<br>

### script(<i>optional</i>)
- script block runs in page
- custom events, attributes can be set in script block
```html
<script>
    /* scripts */
</script>
```

<br>
<br>

# Todo
- [x] enable componenting(V 0.2.0)
    - [ ] component properties
- [x] multi locational data binding(V 0.2.0)
- [x] dataSession (V 0.2.0)
- add vue properties
    - [x] method (V 0.1.0)
    - [x] computed (V 0.2.0)

<br>
<br>

# License
pyvuejs is MIT license

<br>
<br>

# Release History
- V 0.1.0 [2020/07/17]
    - initial commit
<br>

- V 0.2.0 [2020/07/18]
    - enable componenting
    - multi locational data binding
    - add <b>computed</b> binding
    - dataSession

- V 0.2.1 [2020/07/19]
    - change decoration as "@method", "@compute"
    - multi locational strategy changed to IP from idGeneration

- V 0.2.2 [2020/07/19]
    - bug fixes
    - parsing errors if model block is empy

- V 0.2.2.Rev1 [2020/07/19]
    - bug fixes
    - show default favicon correctly

- V 0.2.2.Rev2 [2020/07/20]
    - remove "Variable" model
    - change component's default size to 100% of parent

- V 0.2.2.Rev3
    - depricated
    - revoke changes and upgrade to Rev4

- V 0.2.2.Rev4 [2020/07/20]
    - variables can upload to session by adding ":session" when it's definition
    - session variables can be used in template by calling "sesssion" dictionary

- V 0.2.2.Rev5 [2020/07/20]
    - change component parsing logic
    - component tag format changed to "<component name=\"[componentName]\" />"

- V 0.2.2.Rev6 [2020/07/20]
    - move multi locational strategy to initial viewpoints
    - add event bind decoration as "@event"
        - currently only support for "load", "show" event
    - enabled to import python modules in app's directory
        - base directory of modules is <b>plugins</b>

- V 0.2.2.Rev7 [2020/07/20]
    - change pyvuejs object to class with constructor
    - bug fixed
