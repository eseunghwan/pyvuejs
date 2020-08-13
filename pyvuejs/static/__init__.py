# -*- coding: utf-8 -*-
from . import __path__


static_dir = __path__[0]
view_template = """
<!DOCTYPE html>
<html>
<head>
<link rel="shortcut icon" href="/static/favicon.ico" type="image/x-icon">
<link rel="shortcut icon" href="/public/favicon.ico" type="image/x-icon">
<script type="text/javascript" src="/static/vue.min.js"></script>
<script type="text/javascript" src="/static/axios.min.js"></script>
<link rel="stylesheet" href="/static/pyvue.css">
<script type="text/javascript" src="/static/pyvue.js"></script>
<title>{$title}</title>
<style>
{$style}
</style>
</head>
<body style="width:100vw;height:100vh;margin:0px auto;overflow:hidden;">
{$template}
<!-- <div id="ws_loader" class="ws-loader">
    <div class="ws-loader-img"></div>
</div> -->
<script type="text/javascript">
new PyVue("{$app_url}", "{$selector}");
</script>
</body>
</html>
"""

error_400 = """
<!DOCTYPE html>
<html>
<body style="width:100vw;height:100vh;margin:0px auto;overflow:hidden;">
    <div style="width:100%;height:100%;display:flex;flex-direction:column;text-align:center;">
        <h1>400 Bad Request</h1>
        <h3>Errors on Server</h3>
        <div style="border-bottom:1px solid black;margin:20px 0px;"></div>
        pyvuejs
    </div>
</body>
</html>
<br>
"""

error_404 = """
<!DOCTYPE html>
<html>
<body style="width:100vw;height:100vh;margin:0px auto;overflow:hidden;">
    <div style="width:100%;height:100%;display:flex;flex-direction:column;text-align:center;">
        <h1>404 Not Found</h1>
        <h3>App not found!</h3>
        <div style="border-bottom:1px solid black;margin:20px 0px;"></div>
        pyvuejs
    </div>
</body>
</html>
<br>
"""
