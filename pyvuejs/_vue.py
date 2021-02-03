# -*- coding: utf-8 -*-
import os, signal, sys, vbuild, webbrowser, http
import inspect, importlib
from glob import glob
from bottle import Bottle, static_file, json_dumps
from ._assets import assets_dir


def render_vue(vue_file) -> str:
    rendered = [
        str(vbuild.render(gv))
        for gv in glob(vue_file)
    ]

    if len(rendered) > 1:
        return "\n".join(rendered)
    elif len(rendered) == 1:
        return rendered[0]
    else:
        return ""

def render_vue_as_html(vue_file:str, template_file:str, component_files:str, view_files:str = None, base_style:str = "", title:str = None):
    if title in (None, ""):
        title = os.path.splitext(os.path.basename(vue_file))[0]
    elif "/" in title:
        title = title.split("/")[-1]

    vue_string = render_vue(vue_file)
    components = render_vue(component_files)
    views = "" if view_files == None else render_vue(view_files)

    vue_script = """
    <link rel="stylesheet" href="/pyvuejs/static/pyvuejs.css">
    <script type="text/javascript" src="/pyvuejs/static/vue.min.js"></script>
    <script type="text/javascript" src="/pyvuejs/static/axios.min.js"></script>
    <script type="text/javascript" src="/pyvuejs/static/pyvuejs.router.js"></script>
    <style>
    """ + base_style + """
    </style>
    """ + components + """
    """ + views + """
    """ + vue_string + """
    <""" + title + """ id="app" />
    <script>
        new Vue({ el: '""" + title + """' });
    </script>"""

    with open(template_file, "r", encoding = "utf-8") as tr:
        template = tr.read()

    return template.replace("{$project_name}", title).replace("<App/>", vue_script).replace("<App></App>", vue_script)

def route_vue(bottle:Bottle, endpoint:str, vue_file:str, template_file:str, component_files:str, view_files:str = None, base_style:str = ""):
    endpoint = endpoint if endpoint.startswith("/") else "/" + endpoint
    bottle.route(endpoint, callback = lambda: render_vue_as_html(vue_file, template_file, component_files, view_files, base_style, endpoint[1:]))


class VueRouter(list):
    def __init__(self, routes:list):
        super().__init__(routes)

    def register(self, bottle:Bottle, app_dir:str):
        for route in self:
            route_vue(
                bottle, "/routes" + route["path"],
                os.path.join(app_dir, "src", "views", route["component"] + ".vue"),
                os.path.join(app_dir, "public", "index.html"), os.path.join(app_dir, "src", "components", "*.vue"),
                base_style = vbuild.render(os.path.join(app_dir, "App.vue")).style
            )

class VueConfig:
    # pyvuejs -> pvuejs -> 047372 -> 47372
    def __init__(self, host:str = "0.0.0.0", port:int = 47372, debug:bool = True, open_webbrowser:bool = True):
        self.host, self.port, self.debug, self.open_webbrowser = host, port, debug, open_webbrowser

class VueMap:
    @staticmethod
    def map(callback = None):
        def decorator(callback):
            setattr(callback, "__map__", { "url": "/" + callback.__name__ })
            return callback

        return decorator(callback)

    @staticmethod
    def unmap(callback):
        delattr(callback, "__map__")

    def __callback_to_response(self, callback_name:str):
        may_callback = getattr(self, callback_name)
        if hasattr(may_callback, "__map__"):
            try:
                return json_dumps(may_callback())
            except:
                return json_dumps("")

    def register(self, bottle:Bottle, debug:bool = False):
        bottle.route(
            f"/{self.__class__.__name__}/<callback_name>",
            method = ["GET", "POST"] if debug else "POST",
            callback = lambda callback_name: self.__callback_to_response(callback_name)
        )


class Vue:
    version:str = "2.0.5.post1"
    router:VueRouter = VueRouter([])
    config:VueConfig = VueConfig()

    def __init__(self):
        vbuild.fullPyComp = True
        self.__bottle = Bottle()
        self.__bottle.route("/stop", callback = lambda: os.kill(os.getpid(), signal.SIGTERM))

    @staticmethod
    def use(obj):
        if isinstance(obj, VueRouter):
            Vue.router = obj
        elif isinstance(obj, VueConfig):
            Vue.config = obj

    def map(self, callback, method:str = "GET", group:str = "fn"):
        self.__bottle.route(f"/{group}/{callback.__name__}", method = method.upper(), callback = lambda: json_dumps(callback()))


    def __load_project(self, app_dir:str) -> str:
        public_dir = os.path.join(app_dir, "public")
        self.__load_publics(public_dir)

        self.__load_assets(os.path.join(app_dir, "src", "assets"))
        self.__load_maps(os.path.join(app_dir, "src", "maps"))
        self.__load_router(os.path.join(app_dir, "src"))

        route_vue(
            self.__bottle, "/", os.path.join(app_dir, "App.vue"),
            os.path.join(public_dir, "index.html"),
            os.path.join(app_dir, "src", "components", "*.vue"), os.path.join(app_dir, "src", "views", "*.vue")
        )

    def __load_publics(self, project_public_dir:str):
        if os.path.exists(os.path.join(project_public_dir, "favicon.ico")):
            self.__bottle.route("/favicon.ico", callback = lambda: static_file("favicon.ico", project_public_dir))

        self.__bottle.route(f"/<public_file_name:path>", callback = lambda public_file_name: static_file(public_file_name, project_public_dir))

    def __load_assets(self, project_assets_dir:str):
        self.__bottle.route("/assets/<asset_file_path:path>", callback = lambda asset_file_path: static_file(asset_file_path, project_assets_dir))

    def __load_maps(self, project_maps_dir:str):
        sys.path.append(project_maps_dir)
        for map_file in glob(os.path.join(project_maps_dir, "*.py")):
            map_file_name = os.path.splitext(os.path.basename(map_file))[0]
            for name, attrib in importlib.import_module(map_file_name).__dict__.items():
                if isinstance(attrib, type) and not name == "VueMap":
                    attrib().register(self.__bottle)

        sys.path.remove(project_maps_dir)

    def __load_router(self, project_src_dir:str):
        sys.path.append(project_src_dir)
        importlib.import_module("router")
        sys.path.remove(project_src_dir)

        self.router.register(self.__bottle, os.path.dirname(project_src_dir))

    def serve(self):
        @self.__bottle.route("/pyvuejs/static/<asset_file_path:path>")
        def get_asset_file(asset_file_path:str):
            ext = os.path.splitext(asset_file_path)[1]
            if not ext in (".py"):
                return static_file(asset_file_path, assets_dir)
            else:
                return ""

        self.__bottle.route("/favicon.ico", callback = lambda: static_file("favicon.ico", assets_dir))

        self.__load_project(os.getcwd())

        if self.config.open_webbrowser:
            webbrowser.open_new(f"http://127.0.0.1:{self.config.port}/")

        self.__serve()

    def __serve(self):
        try:
            self.__bottle.run(host = self.config.host, port = self.config.port, quiet = not self.config.debug)
        except OSError:
            if "address already in use" in str(sys.exc_info()[1]).lower():
                http.client.HTTPConnection("127.0.0.1", self.config.port).request("GET", "/stop")
                self.__serve()
