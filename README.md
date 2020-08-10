<p align="center">
<img src="https://github.com/eseunghwan/pyvuejs/blob/master/logo.png?raw=true" width=250 />
<br>
<a href="https://pypi.python.org/pypi/pyvuejs">
<img src="https://img.shields.io/pypi/v/pyvuejs.svg" /></a>
<a href="https://travis-ci.org/eseunghwan/pyvuejs"><img src="https://travis-ci.org/eseunghwan/pyvuejs.svg?branch=master" /></a>
</p>
<br><br>

# Install
### using pip
```powershell
pip install pyvuejs
```
<br><br>

# Usage
### start server by <b>main.py</b> file in project directory
```powershell
python .\main.py
```
<br><br>

# Config editing guide
- config file has 2 dictionaries
    - pages: information of apps
    - server: server host, port information
```python
pages = {
    "sample": {
        # entry, vue, url are required
        "entry": "src/app/main.py",
        "vue": "src/app/index.vue", 
        "url": "/sample",
        "title": "sample!"
    }
}

server = {
    # host and port are not required
    "host": "0.0.0.0",
    "port": 8080
}
```
<br><br>

# VUE editing guide
### same as vue.js, can support by linting
- for now, <b>template</b>, <b>style</b> blocks are supported
```html
<template>
    <div id="sample">
        <p>{{ text }}</p>
    </div>
</template>

<style>
    div#sample {
        width: 100%;
        height: 100%;
    }
</style>
```
<br><br>

# App model editing guide
- Model defines in <b>main.py</b> in app directory
- same syntax as Vue.js javascript defines
- get object by <b>export</b> property
```python
from pyvuejs import Vue

class sample():
    def data(self):
        # return as dictionary
        return {
            "text": "hello, pyvuejs!"
        }

    def methods(self):
        def change_text(self):
            self.text = "I'm changed!"

        # return as dictionary
        return {
            "change_text": change_text
        }

# "__export__" must be defined
__export__ = Vue.createApp(sample).mount("#sample")
```
<br>
<br>

# Component editing guide
- component defines in <b>component</b> directory
- name of python file is not important
- components are registered as global component
- get object by <b>export</b> property
```python
from pyvuejs import Vue

class sample():
    # props are list only
    props = [ "label" ]
    # template is required
    template = "<label>{{ label }}</label>"

# "__export__" must be defined
__export__ = Vue.component("sample-label", sample)
```
<br><br>

# Todo
- [ ] <b>method</b>, <b>created</b>, <b>mounted</b> of component

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

- V 0.4.2 [2020/07/29]
    - change webview frontend from pycefsharp to pywebview

- V 0.4.3 [2020/07/29]
    - change webview frontend from pywebview to PySide2
    - child window appears properly

- V 0.5.0 [2020/08/10]
    - BIG CHANGES!
        - server changes to <b>bottle</b>
        - change project structure more likely to Vue.js
        - separate cli to <b>pyvuejs-cli</b>
