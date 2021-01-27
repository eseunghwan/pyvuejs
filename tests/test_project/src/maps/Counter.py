# -*- coding: utf-8 -*-
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
