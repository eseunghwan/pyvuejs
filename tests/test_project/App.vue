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

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
}

#nav {
    padding: 30px;
}

#nav a {
    font-weight: bold;
    color: #2c3e50;
}

#nav a.router-link-exact-active {
    color: #42b983;
}
</style>

<script lang="python">
class Component:
    def __init__(self):
        self.page = "Home"

    def show_home(self):
        self.page = "Home"

    def show_about(self):
        self.page = "About"

    def show_counter(self):
        self.page = "Counter"
</script>
