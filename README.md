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
python -m pyvuejs init --app=sampleApp

[console output]
[pyvuejs | 2020-07-21T20:32:24Z] INFO: Creating pyvuejs application...
[pyvuejs | 2020-07-21T20:32:24Z] INFO: Extracting template files...
[pyvuejs | 2020-07-21T20:32:24Z] INFO: App "sampleApp" is ready!
```
<br>

### move to project directory and start with cli
- default host = "0.0.0.0", port = 8000
- both <b>host</b> and <b>port</b> are positional arguments
```powershell
python .\manage.py run --host=127.0.0.1 --port=8080

[console output]
[pyvuejs | 2020-07-21T20:54:09Z] INFO: Starting pyvuejs application...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Prepare Server to run app...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Setting function routing points...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Setting socket routing points...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Routing points are ready!

[pyvuejs | 2020-07-21T20:54:10Z] INFO: Interpreting app...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Interpreting view files...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: hello.pvue has been interpreted
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Finished!

[pyvuejs | 2020-07-21T20:54:10Z] INFO: Linking static files to server...
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Finished!

[pyvuejs | 2020-07-21T20:54:10Z] INFO: App has been ready!

[pyvuejs | 2020-07-21T20:54:10Z] INFO: Server is ready!

[pyvuejs | 2020-07-21T20:54:10Z] INFO: Server started on "0.0.0.0:8080"
[pyvuejs | 2020-07-21T20:54:10Z] INFO: Please check Devtool to show data transfers

[web console output]
[pyvuejs | 2020-07-21T21:01:33Z] INFO: Model 127.0.0.1/main/App created
[pyvuejs | 2020-07-21T21:01:33Z] INFO: View 127.0.0.1/main loaded
[pyvuejs | 2020-07-21T21:01:33Z] INFO: Model 127.0.0.1/hello2/App created
[pyvuejs | 2020-07-21T21:01:33Z] INFO: View 127.0.0.1/hello2 loaded
[pyvuejs | 2020-07-21T21:01:42Z] INFO: Variables of 127.0.0.1/hello2/App updated
[pyvuejs | 2020-07-21T21:01:43Z] INFO: Variables of 127.0.0.1/main/App updated
```
<br>

### start standalone mode
- switch mode to <b>standalone</b>
- size of window can be adjusted by <b>window-size</b> argument
- host and port options are available
- using <b>PySide2's WebEngineView</b>
```powershell
python .\manage.py run --host=127.0.0.1 --port=8080 --mode=standalone --window-size=900,600

[console output]
[pyvuejs | 2020-07-22T00:13:01Z] INFO: Start server on background...
[pyvuejs | 2020-07-22T00:13:01Z] INFO: Setting up webview...
[pyvuejs | 2020-07-22T00:13:01Z] INFO: Starting pyvuejs application...
[pyvuejs | 2020-07-22T00:13:03Z] INFO: Webview is loaded
[pyvuejs | 2020-07-22T00:13:09Z] INFO: Shutting down background server...
```
<br>

### stop server from cli
- server can be closed by cli
```powershell
python .\manage.py stop

[server console output]
[pyvuejs | 2020-07-21T21:01:44Z] INFO: App is shutting down...
```
<br>

### create, remove resources from cli
- plugin, folder, file is available by type argument
- default directory of plugin is <b>plugins</b>
- default directory of other resources is <b>app root</b>
```powershell
<# create #>
python .\manage.py create --type=plugin --name=plugin1

[console output]
[pyvuejs | 2020-07-21T21:05:55Z] INFO: Creating plugin plugin1...
[pyvuejs | 2020-07-21T21:05:55Z] INFO: Plugin plugin1 is ready!

<# remove #>
python .\manage.py remove --type=plugin --name=plugin1

[console output]
[pyvuejs | 2020-07-21T21:09:09Z] INFO: Removing plugin plugin1...
[pyvuejs | 2020-07-21T21:09:09Z] INFO: Plugin plugin1 is removed!
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
- [ ] sync variables during method runs
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
        - pyvuejs calls other view's models also
<br>

- V 0.3.0 [2020/07/21]
    - change backend server to flask from quart
    - changes in <b>requirements.txt</b>
    - bug fixed
        - session datas are not sync from view to model

- V 0.3.0.Rev1 [2020/07/21]
    - bug fixed
        - session datas changed in vue model are not sync to model

- V 0.3.1 [2020/07/21]
    - cli changed
        - "init" command is available from module cli
        - "run", "stop", "create", "remove" commands are moved to <b>manage.py</b>
    - logger added
        - server logs <b>server-side</b> loggings only
        - client(web) logs <b>client-side</b> loggings only

- V 0.3.2 [2020/07/22]
    - standalone mode added
        - use PySide2 WebEngineView as UI
    - "logging" option added
        - if <b>enable</b>, server log to console
        - if not, server doesn't log to console

- V 0.3.2.Rev1 [2020/07/22]
    - webview window can be invoked from model with name <b>webview</b>
