# -*- coding: utf-8 -*-
import os
from . import __path__

baseView = """
<!DOCTYPE HTML5>
<html>
    <head>
        <link rel="shortcut icon" href="/static/favicon.ico">
        <link rel="shortcut icon" href="/app/favicon.ico">
        <link rel="stylesheet" href="/static/pyvuejs.css">
        <script type="text/javascript" src="/static/vue.min.js"></script>
        <script type="text/javascript" src="/static/pyvuejs.elements.js"></script>
        <script type="text/javascript" src="/static/pyvuejs.utils.js"></script>
        <script type="text/javascript" src="/static/pyvuejs.js"></script>
        {$viewResource}
        <style>
            {$viewStyle}
        </style>
    </head>
    <body style="width:100vw;height:100vh;margin:0px auto;overflow:hidden;">
        {$viewTemplate}

        <script>
            (new pyvuejs("{$viewId}", "{$viewName}", {$viewModels})).init();
        </script>
    </body>
</html>
"""
project_template = os.path.join(__path__[0], "project_template.zip")
app_template = os.path.join(__path__[0], "app_template.zip")

del __path__
del os
