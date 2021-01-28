# -*- coding: utf-8 -*-
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
