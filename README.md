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
python -m pyvuejs create-project --name=sample_project

[console output]
[pyvuejs | 2020-07-28T23:27:49Z] INFO: Creating pyvuejs project...
[pyvuejs | 2020-07-28T23:27:49Z] INFO: Extracting template files...
[pyvuejs | 2020-07-28T23:27:49Z] INFO: Project "sample_project" is ready!
```
<br>

### manage apps with cli
- <b>main</b> app cannot be removed
```powershell
<# create #>
python .\manage.py create-app --name=sample_app

[console output]
[pyvuejs | 2020-07-28T23:28:23Z] INFO: Creating pyvuejs app...
[pyvuejs | 2020-07-28T23:28:23Z] INFO: Extracting template files...
[pyvuejs | 2020-07-28T23:28:23Z] INFO: App "sample_app" is ready!

<# remove #>
python .\manage.py remove-app --name=sample_app

[console output]
[pyvuejs | 2020-07-28T23:28:55Z] INFO: Removing app "sample_app"...
[pyvuejs | 2020-07-28T23:28:55Z] INFO: App "sample_app" removed!
```
<br>

### start project with cli
- default host = "0.0.0.0", port = 8000
- both <b>host</b> and <b>port</b> are positional arguments
```powershell
python .\manage.py start --host=127.0.0.1 --port=8000

[console output]
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Preparing server...

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Setting routing points...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Setting view/component points...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Setting function points...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: finished

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Interpreting project "sample_project"...

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Interpreting app "main"...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Interpreting pvue file...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: finished
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Interpreting models...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Model mainApp loaded
[pyvuejs | 2020-07-28T23:31:45Z] INFO: finished

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Linking static to server...
[pyvuejs | 2020-07-28T23:31:45Z] INFO: finished

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Project is ready!

[pyvuejs | 2020-07-28T23:31:45Z] INFO: Server started on "http://127.0.0.1:8000/"
[pyvuejs | 2020-07-28T23:31:45Z] INFO: Please check Devtool to show data transfers
Running on http://0.0.0.0:8000 (CTRL + C to quit)

[web console output]
[pyvuejs | 2020-07-28T23:32:40Z] INFO: Model 127.0.0.1/main/mainApp created
[pyvuejs | 2020-07-28T23:32:40Z] INFO: View 127.0.0.1/main loaded
```
<br>

### start project standalone mode
- switch mode to <b>standalone</b>
- host and port options are available
- using <b>pycefsharp</b>
```powershell
python .\manage.py start --host=127.0.0.1 --port=8000 --mode=standalone

[console output]
[pyvuejs | 2020-07-28T23:38:37Z] INFO: Start server on background...
[pyvuejs | 2020-07-28T23:38:37Z] INFO: Setting up webview...
[pyvuejs | 2020-07-28T23:38:37Z] INFO: Webview is loaded
Running on http://0.0.0.0:8000 (CTRL + C to quit)
[pyvuejs | 2020-07-28T23:39:26Z] INFO: Shutting down background server...

[pycefsharp console output]
[0728/233838.805:INFO:CONSOLE(14)] "[pyvuejs | 2020-07-28T23:38:38Z] INFO: Model 127.0.0.1/main/mainApp created", source: http://127.0.0.1:8000/static/pyvuejs.utils.js (14)
[0728/233838.806:INFO:CONSOLE(14)] "[pyvuejs | 2020-07-28T23:38:38Z] INFO: View 127.0.0.1/main loaded", source: http://127.0.0.1:8000/static/pyvuejs.utils.js (14)
```
<br>

### stop server from cli
- server can be closed by cli
```powershell
python .\manage.py stop

[server console output]
[pyvuejs | 2020-07-28T23:43:35Z] INFO: Server is shutting down...
```
<br>
<br>

# VIEW editing guide
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
        <pvue-component endpoint="[componentName]"></pvue-component>
    </div>
</template>
```
<br>

### resources(<i>optional</i>)
- resources block loads app's static files
- app's static url is <b>"/app"</b>
```html
<resources>
    <!-- css -->
    <link rel="stylesheet" href="/app/[staticFileName]">
    <!-- js -->
    <script type="text/javascript" src="/app/[staticFileName]"></script>
</resources>
```
<br>

### style(<i>optional</i>)
- style block is style part of template block
```html
<style>
div#mainApp {
    /* styles */
}
</style>
```
<br>
<br>

# Model editing guide
- Model base class is in <b>pyvuejs.models</b>
- bindings are in <b>pyvuejs.binders</b>
```python
from pyvuejs.models import Model
from pyvuejs.binder import model_variable, event, method

class mainApp(Model):
    """variables
    - model_variable: variable for model locally
    - session_variable: variable for session(global)
    """
    username:str = model_variable("")

    """events
    - load: when model init
    - show: when view show
    """
    @event("load")
    def onload(self):
        print("hello, pyvuejs!")

    """methods
    any method in Model decorated "method"
    """
    @method
    def change_username(self):
        self.username = "pyvuejs"
```
<br>
<br>

# Todo
- [x] enable componenting(V 0.2.0)
    - [ ] component properties
- [x] multi locational data binding(V 0.2.0)
- [x] dataSession (V 0.2.0)
- [ ] sync variables during method runs
    - only session available
- add vue properties
    - [x] method (V 0.1.0)
    - ~~[x] computed (V 0.2.0)~~
        - removed (V 0.4.0)

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

- V 0.3.2.Rev2 [2020/07/22]
    - bug fixed
        - multiple session datas upload correctly

- V 0.3.3 [2020/07/22]
    - bug fixed
        - model's native functions got erros during interpreting
    - add <b>pyvue-component</b> tag and change <b>component</b> to <b>pyvue-component</b>
        - format change to normal html format, "<pyvue-component endpoint=\"componentName\"></pyvue-component>"
    - <b>webview</b> attribute changed to <b>appView</b>
    - creating a new WebView window is available from model

- V 0.3.3.Rev1 [2020/07/22]
    - bug fixed
        - decorator text was miss-parsed

- V 0.3.4 [2020/07/22]
    - change UI module from PySide2 to pycefsharp
        - appView can be invoked, too
<br>

- V 0.4.0 [2020/07/28]
    - change structure of project
        - project now managed by app
            - app has single <b>view.html</b> file
            - app can has multiple models in <b>models.py</b>
        - project information managed by <b>.config</b> file
    - cli changed
        - cli provides as follows
            - <b>create-project</b>
            - <b>create-app</b>
            - <b>remove-app</b>
            - <b>start</b>
            - <b>stop</b>

- V 0.4.1 [2020/07/29]
    - remove unnecessary requirements
    - change session refresh interval from 0.5s to 0.1s
