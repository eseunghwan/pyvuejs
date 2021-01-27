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

    def up_count(self):
        self.count += 1

    def down_count(self):
        if self.count > 0:
            self.count -= 1
</script>
