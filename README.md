<p align="center">
<img src="https://github.com/eseunghwan/pyvuejs/blob/master/logo.png?raw=true" width=250 />
<br>
<a href="https://pypi.python.org/pypi/pyvuejs">
<img src="https://img.shields.io/pypi/v/pyvuejs.svg" /></a>
<a href="https://travis-ci.org/eseunghwan/pyvuejs"><img src="https://travis-ci.org/eseunghwan/pyvuejs.svg?branch=master" /></a>
</p>
<br><br>

# RE:Newal!
- changed project style more silimar to vuejs 2.x template
- use vue file by <b>vbuild</b>
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
python ./main.py
```
<br><br>

# serve configurations
config update by Vue.use in <b>main.py</b>
- parameters
    - host[str]: host url of server(default: "0.0.0.0")
    - port[int]: port number of server(default: 47372)
    - debug[bool]: flag of show bottle log(default: True)
    - open_webbrowser[bool]: flag of open browser when start(default: True)
```python
Vue.use(
    VueConfig(
        host = "0.0.0.0",
        port = 47372,
        debug = True,
        open_webbrowser = True
    )
)
```
<br><br>

# view/component editing guide
### same as vue.js, can support by linting
- for now, <b>template</b>, <b>style</b>, <b>script</b> blocks are supported
- more information on [vbuild](https://github.com/manatlan/vbuild) and [vbuild python document](https://github.com/manatlan/vbuild/blob/master/doc/PyComponent.md)
```html
<!-- template block -->
<template>
    <div>
        <label>{{ count }}</label>
        <div>
            <button style="margin-right:10px;" v-on:click="up_count">up</button>
            <button v-on:click="down_count">down</button>
        </div>
    </div>
</template>
<!-- style block -->
<style scoped>
button {
    width: 80px;
}
</style>
<!-- script block -->
<script lang="python">
class Component:
    def __init__(self):
        self.count = 0

    def up_count(self):
        self.count += 1

    def down_count(self):
        if self.count > 0:
            self.count -= 1
</script>
```
<br><br>

# use view/component
just call name in other view
```html
<template>
    <div id="app">
        <div id="nav">
            <router-link to="/Home">Home</router-link> |
            <router-link to="/About">About</router-link> |
            <router-link to="/Counter">Counter</router-link>
        </div>
        <router-view/>
    </div>
</template>
```
<br><br>

# events mapping
define map class and map functions in each file of <b>maps</b>
- if <b>debug</b> option in config, functions can be reached by "GET" and "POST". else, "POST" only
```python
from pyvuejs import VueMap

class Counter(VueMap):
    count = 0

    @VueMap.map
    def get_count(self):
        return self.count

    @VueMap.map
    def up_count(self):
        self.count += 1

    @VueMap.map
    def down_count(self):
        if self.count > 0:
            self.count -= 1
```
<br><br>

# routes
define route <b>path</b> and <b>component</b> in <b>router.py</b>
```python
from pyvuejs import Vue, VueRouter

Vue.use(VueRouter([
    {
        "path": "/About",
        "component": "About"
    },
    {
        "path": "/Home",
        "component": "Home"
    },
    {
        "path": "/Counter",
        "component": "Counter"
    }
]))
```
<br><br>

# Todo
- [x] <b>routes</b>

<br><br>

# License
pyvuejs is MIT license

<br>
