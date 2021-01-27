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
            <label v-on:click="show_home">Home</label> |
            <label v-on:click="show_about">About</label> | 
            <label v-on:click="show_counter">Counter</label>
        </div>
        <Home v-if="page == 'Home'" />
        <About v-else-if="page == 'About'" />
        <Counter v-else-if="page == 'Counter'" />
        <div v-else></div>
    </div>
</template>
```
<br><br>

# function mapping
call map on <b>main.py</b>
- parameters
    - callback[required]: callback to map
    - method[optional(default="GET")]: method of map
    - group[optional(default="fn")]: url group of map
```python
def some_callback():
    """
    callback job
    """

Vue().map(
    some_callback, method = "GET", group = "fn"
).serve()
```

# Todo
- [ ] <b>routes</b>

<br>
<br>

# License
pyvuejs is MIT license

<br>
<br>

# Release History
### 2.0.0
- renewal version1
