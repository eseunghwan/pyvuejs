<template>
    <div>
        <label>{{ count }}</label>
        <div>
            <button style="margin-right:10px;" v-on:click="up_count">up</button>
            <button v-on:click="down_count">down</button>
        </div>
    </div>
</template>

<style scoped>

button {
    width: 80px;
}

</style>

<script lang="python">
class Component:
    def __init__(self):
        self.count = 0

    def MOUNTED(self):
        self.get_count()
    
    def update_count(self, req):
        self.count = req.data

    def get_count(self):
        axios.post("/Counter/get_count").then(self.update_count)

    def up_count(self):
        axios.post("/Counter/up_count").then(self.get_count)

    def down_count(self):
        axios.post("/Counter/down_count").then(self.get_count)
</script>
