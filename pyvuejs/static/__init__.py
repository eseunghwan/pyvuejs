# -*- coding: utf-8 -*-
import os
from . import __path__

baseView = """
<!DOCTYPE HTML5>
<html>
    <head>
        <link rel="shortcut icon" href="/static/favicon.ico">
        <link rel="icon" href="/static/favicon.png">
        <link rel="shortcut icon" href="/app/favicon.ico">
        <link rel="icon" href="/app/favicon.png">
        <script type="text/javascript" src="/static/socket.io.dev.js"></script>
        <script type="text/javascript" src="/static/vue.min.js"></script>
        <script type="text/javascript" src="/static/pyvuejs.js"></script>
        {$viewResource}
        <style>
            {$viewStyle}
        </style>
        <script>
            {$viewScript}
        </script>
    </head>
    <body style="width:100vw;height:100vh;margin:0px auto;overflow:hidden;">
        {$viewBody}

        <script>
            (new pyvuejs("{$viewId}", "{$viewName}", "view", ["{$viewModels}"])).init();
        </script>
    </body>
</html>
"""
templateZip = os.path.join(__path__[0], "template.zip")

del __path__
del os
