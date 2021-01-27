# -*- coding: utf-8 -*-
import os, vbuild, webbrowser
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

class Vue:
    version:str = "2.0.0"

    def __init__(self):
        self.__router, self.__config = VueRouter([]), VueConfig()
        self.__bottle = Bottle()

    def use(self, obj):
        if isinstance(obj, VueRouter):
            self.__router = obj
        elif isinstance(obj, VueConfig):
            self.__config = obj

        return self

    def __use_router(self):
        for route in self.__router:
            print(route)

    def __use_config(self):
        print(self.__config)

    def __load_project(self, app_dir:str) -> str:
        public_dir = os.path.join(app_dir, "public")
        self.__bottle.route("/<public_file_path:path>", callback = lambda public_file_path: static_file(public_file_path, public_dir))

        self.__load_assets(os.path.join(app_dir, "src", "assets"))

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

            return template.replace("<App/>", app_script).replace("<App></App>", app_script)


    def __load_assets(self, project_assets_dir:str):
        self.__bottle.route("/assets/<asset_file_path:path>", callback = lambda asset_file_path: static_file(asset_file_path, project_assets_dir))

    def __load_components(self, project_components_dir:str) -> str:
        return str(vbuild.render(os.path.join(project_components_dir, "*.vue")))

    def __load_views(self, project_views_dir:str) -> str:
        return str(vbuild.render(os.path.join(project_views_dir, "*.vue")))

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

        self.__bottle.run(host = self.__config.host, port = self.__config.port, quiet = not self.__config.debug)
