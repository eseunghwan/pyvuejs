# -*- coding: utf-8 -*-
import os, signal, sys, vbuild, webbrowser, http
import inspect, importlib
from glob import glob
from bottle import Bottle, static_file, json_dumps
from ._assets import assets_dir


class VueRouter(list):
    def __init__(self, routes:list):
        super().__init__(routes)

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

    def register(self, bottle:Bottle):
        bottle.route(f"/{self.__class__.__name__}/<callback_name>", method = ["GET", "POST"], callback = lambda callback_name: self.__callback_to_response(callback_name))
            


class Vue:
    version:str = "2.0.3"

    def __init__(self):
        vbuild.fullPyComp = True
        self.__router, self.__config = VueRouter([]), VueConfig()
        self.__bottle = Bottle()
        self.__bottle.route("/stop", callback = lambda: os.kill(os.getpid(), signal.SIGTERM))

    def use(self, obj):
        if isinstance(obj, VueRouter):
            self.__router = obj
        elif isinstance(obj, VueConfig):
            self.__config = obj

        return self

    def map(self, callback, method:str = "GET", group:str = "fn"):
        self.__bottle.route(f"/{group}/{callback.__name__}", method = method.upper(), callback = lambda: json_dumps(callback()))

    def __load_project(self, app_dir:str) -> str:
        public_dir = os.path.join(app_dir, "public")
        self.__load_publics(public_dir)

        self.__load_assets(os.path.join(app_dir, "src", "assets"))
        self.__load_maps(os.path.join(app_dir, "src", "maps"))

        @self.__bottle.route("/")
        def route_app():
            with open(os.path.join(public_dir, "index.html"), encoding = "utf-8") as tr:
                template = tr.read()

            components = self.__load_components(os.path.join(app_dir, "src", "components"))
            views = self.__load_views(os.path.join(app_dir, "src", "views"))
            main_app = str(vbuild.render(os.path.join(app_dir, "App.vue")))
            app_script = """
            <script type="text/javascript" src="/pyvuejs/static/vue.min.js"></script>
            <script type="text/javascript" src="/pyvuejs/static/axios.min.js"></script>
            """ + components + """
            """ + views + """
            """ + main_app + """
            <App/>
            <script>
            new Vue({ el: "app" })
            </script>"""

            return template.replace(
                "{$project_name}", os.path.basename(app_dir)
            ).replace("<App/>", app_script).replace("<App></App>", app_script)


    def __load_publics(self, project_public_dir:str):
        if os.path.exists(os.path.join(project_public_dir, "favicon.ico")):
            self.__bottle.route("/favicon.ico", callback = lambda: static_file("favicon.ico", project_public_dir))

        for public_file_glob in glob(os.path.join(project_public_dir, "**"), recursive = True):
            public_file_path = os.path.join(project_public_dir, public_file_glob)
            if not os.path.isdir(public_file_path):
                self.__bottle.route(f"/public/{public_file_glob}", callback = lambda: static_file(public_file_glob, project_public_dir))

    def __load_assets(self, project_assets_dir:str):
        self.__bottle.route("/assets/<asset_file_path:path>", callback = lambda asset_file_path: static_file(asset_file_path, project_assets_dir))

    def __load_components(self, project_components_dir:str) -> str:
        return str(vbuild.render(os.path.join(project_components_dir, "*.vue")))

    def __load_views(self, project_views_dir:str) -> str:
        return str(vbuild.render(os.path.join(project_views_dir, "*.vue")))

    def __load_maps(self, project_maps_dir:str):
        sys.path.append(project_maps_dir)
        for map_file in glob(os.path.join(project_maps_dir, "*.py")):
            map_file_name = os.path.splitext(os.path.basename(map_file))[0]
            for name, attrib in importlib.import_module(map_file_name).__dict__.items():
                if isinstance(attrib, type) and not name == "VueMap":
                    attrib().register(self.__bottle)

        sys.path.remove(project_maps_dir)

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

        if self.__config.open_webbrowser:
            webbrowser.open_new(f"http://127.0.0.1:{self.__config.port}/")

        self.__serve()

    def __serve(self):
        try:
            self.__bottle.run(host = self.__config.host, port = self.__config.port, quiet = not self.__config.debug)
        except OSError:
            if "address already in use" in str(sys.exc_info()[1]).lower():
                http.client.HTTPConnection("127.0.0.1", self.__config.port).request("GET", "/stop")
                self.__serve()
