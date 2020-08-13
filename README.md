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

# App registering guide
- App registers in <b>main.py</b> in `project directory`/main.py
- same syntax as Vue.js javascript defines
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

Vue.createApp(sample).mount("#sample")

"""
and many other apps...
"""
```
<br>
<br>

# Component editing guide
- component defines in <b>component</b> directory
- name of python file is not important
- <b>no global components</b>
```python
from pyvuejs import Vue

class sample():
    # props are list only
    props = [ "label" ]
    # template is required
    template = "<label>{{ label }}</label>"

Vue.component("sample-label", sample)
```
<br><br>

# Routing editing guide
- Routing options register in `project directory`/router/init.py
```python
from pyvuejs import Vue

Vue.Router({
    # url of public files can be registered
    "public": {
        "url": "/public"
    },
    # url of app and components can be registered
    "sample": {
        # url is required
        "url": "/sample",
        # names of components to use
        "components": [ "sample-label" ]
    }
})
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
change log of `Rev` versions deleted
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
<br>

- V 0.3.0 [2020/07/21]
    - change backend server to flask from quart
    - changes in <b>requirements.txt</b>
    - bug fixed
        - session datas are not sync from view to model

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

- V 0.3.3 [2020/07/22]
    - bug fixed
        - model's native functions got erros during interpreting
    - add <b>pyvue-component</b> tag and change <b>component</b> to <b>pyvue-component</b>
        - format change to normal html format, "<pyvue-component endpoint=\"componentName\"></pyvue-component>"
    - <b>webview</b> attribute changed to <b>appView</b>
    - creating a new WebView window is available from model

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
<br>
<hr>
<b>※ WARNING: PROJECT SKELETON CHANGED A LOT FROM V0.5!</b>

- V 0.5.0 [2020/08/10]
    - BIG CHANGES!
        - server changes to <b>bottle</b>
        - change project structure more likely to Vue.js
        - separate cli to <b>pyvuejs-cli</b>

- V 0.5.1 [2020/08/10]
    - remove unsed requirement <b>bottle-websocket</b>
    - set server config by default if not configured
    - add <b>default_app</b> parameter to standalone server method
    - add <b>show_messagebox</b> method to webview
        - not receive result now

- V 0.5.1 [2020/08/11]
    - remove <b>config.py</b>
    - change app structure
        - register app in `project directory`/src/main.py
    - register routing infos in `project directory`/src/router/init.py
