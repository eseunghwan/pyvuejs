# -*- coding: utf-8 -*-
from pyvuejs import Vue, VueConfig

Vue().use(
    VueConfig(open_webbrowser = True)
).serve()
