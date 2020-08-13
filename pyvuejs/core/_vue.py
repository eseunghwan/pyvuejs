# -*- coding: utf-8 -*-
import os, sys
from collections import OrderedDict
from typing import Dict
from bottle import get, post, request, response, json_dumps, redirect
import importlib

from ..static import view_template
from ..handlers import VueException
from ._server import Server


class VueLib():
    def __init__(self, vue_file:str):
        self.__name = os.path.splitext(os.path.basename(vue_file))[0]

        with open(os.path.abspath(vue_file), "r", encoding = "utf-8") as vue_read:
            vue_text = vue_read.read()

            for block_name in ("template", "style"):
                block_start, block_end = "<{}>".format(block_name), "</{}>".format(block_name)

                if block_start in vue_text and block_end in vue_text:
                    setattr(self, f"__{block_name}", vue_text.split(block_start)[1].split(block_end)[0])
                else:
                    setattr(self, f"__{block_name}", "")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def template(self) -> str:
        return getattr(self, "__template")

    @property
    def style(self) -> str:
        return getattr(self, "__style")

class VueApp():
    _data = []
    _methods = []

    def __init__(self, vue_lib:VueLib):
        self.__selector = ""
        self.__vue = vue_lib

    def _get_data(self, name:str):
        if name in self._data:
            return getattr(self, name)
        else:
            return None

    def _set_data(self, name:str, value):
        if name in self._data:
            setattr(self, name, value)

    def _get_method(self, name:str):
        if name in self._methods:
            return getattr(self, name)
        else:
            return None

    def _call_method(self, name:str):
        if name in self._methods:
            self._get_method(name)(self)

    def created(self):
        pass

    def mounted(self):
        pass

    def mount(self, selector:str):
        self.__selector = selector
        return self

    def render(self):
        return view_template.replace(
            "{$selector}", self.__selector
        ).replace(
            "{$template}", self.__vue.template
        ).replace(
            "{$style}", self.__vue.style
        )
        # .replace(
        #     "{$app_url}", self.__app_config["url"]
        # ).replace(
        #     "{$title}", self.__app_config["title"]
        # )

class VueComponent():
    props:list = []
    template:str = ""
    style:str = ""

class VueModel():
    def __init__(self):
        self.__is_inited = False

    @property
    def selector(self) -> str:
        return self.__selector

    def data(self) -> dict:
        pass

    def methods(self) -> dict:
        pass

    def created(self):
        pass

    def mounted(self):
        pass

    def mount(self, selector:str):
        if not self.__is_inited:
            self.__is_inited = True

            fn_data = getattr(self, "data")
            for key, value in fn_data().items():
                def getter(this, name = key):
                    return this._data[name]

                def setter(this, other, name = key):
                    this._data[name] = other

                setattr(self, key, property(getter, setter))
                exec("self.{} = value".format(key))

            fn_methods = getattr(self, "methods")
            for key, value in fn_methods().items():
                setattr(self, key, value)

            delattr(self.__class__, "data")
            delattr(self.__class__, "methods")
            setattr(self, "_data", fn_data())
            setattr(self, "_methods", fn_methods())

        self.__selector = selector

        return self

class VueUtils:
    apps:Dict[str, VueApp] = OrderedDict()
    components:Dict[str, VueComponent] = OrderedDict()

    @staticmethod
    def importVue(vue_file:str) -> VueLib:
        return VueLib(vue_file)

    @staticmethod
    def createApp(vue_lib:VueLib, app_class):
        try:
            cls = app_class()
        except:
            cls = app_class

        app = VueApp(vue_lib)

        if hasattr(cls, "data"):
            data = getattr(cls, "data")()
            setattr(app, "_data", list(data.keys()))
            for key, value in data.items():
                setattr(app, key, value)

        if hasattr(cls, "methods"):
            methods = getattr(cls, "methods")()
            setattr(app, "_methods", list(methods.keys()))
            for key, value in methods.items():
                setattr(app, key, value)

        if hasattr(cls, "created"):
            setattr(app, "created", getattr(cls, "created"))

        if hasattr(cls, "mounted"):
            setattr(app, "mounted", getattr(cls, "mounted"))

        VueUtils.apps[vue_lib.name] = app

        return app

    @staticmethod
    def component(name:str, component_cls) -> VueComponent:
        try:
            cls = component_cls()
        except:
            cls = component_cls

        if not hasattr(cls, "template"):
            raise VueException("Component must have \"template\"!")

        component = VueComponent()

        if hasattr(cls, "props"):
            setattr(component, "props", getattr(cls, "props"))

        if hasattr(cls, "template"):
            setattr(component, "template", getattr(cls, "template"))

        if hasattr(cls, "style"):
            setattr(component, "style", getattr(cls, "style"))

        VueUtils.components[name] = component

    @staticmethod
    def Router(route_options:dict):
        src_dir = os.getcwd()
        project_dir = os.path.dirname(src_dir)

        route_keys = list(VueUtils.apps.keys()) + list(VueUtils.components.keys()) + [ "public" ]
        for route_name, route_info in route_options.items():
            if not route_name in route_keys:
                raise VueException("Unregistered app!")

            if not "url" in route_info.keys():
                raise VueException("\"url\" property is not defined!")

            if route_name == "public":
                @get(f"{route_info['url']}/<public_file>")
                def serve_public_file(public_file:str):
                    file_ext = os.path.splitext(public_file)[1][1:]
                    public_file = os.path.join(project_dir, "public", public_file)

                    if os.path.exists(public_file):
                        if file_ext == "ico":
                            response.set_header("Content-type", "image/x-icon")
                            return open(public_file, "rb").read()
                        elif file_ext == "js":
                            response.set_header("Content-type", "text/javascript")
                        else:
                            response.set_header("Content-type", "text/{}".format(file_ext))

                        return open(public_file, "r", encoding = "utf-8").read()
                    else:
                        return "public files: " + ", ".join(os.listdir(os.path.join(project_dir, "public")))

            elif route_name in VueUtils.apps.keys():
                if not "components" in route_info.keys():
                    route_info["components"] = []

                def register_route_app(app_name:str, app_url:str, component_names:list):
                    @get(app_url)
                    def serve_app_render():
                        response.set_header("content-type", "text/html")
                        return VueUtils.apps[app_name].render().replace(
                            "{$app_url}", app_url
                        ).replace(
                            "{$title}", app_name
                        )

                    @get(f"{app_url}/init")
                    def init_app_vue():
                        return json_dumps({
                            "data": {
                                name: VueUtils.apps[app_name]._get_data(name)
                                for name in VueUtils.apps[app_name]._data
                            },
                            "methods": VueUtils.apps[app_name]._methods,
                            "components": {
                                component_name: {
                                    "props": VueUtils.components[component_name].props,
                                    "template": VueUtils.components[component_name].template,
                                    "style": VueUtils.components[component_name].style
                                }
                                for component_name in component_names
                            }
                        })

                    @get(f"{app_url}/data/get")
                    def fn_send_data_to_vue():
                        return json_dumps({ "data": {
                                name: VueUtils.apps[app_name]._get_data(name)
                                for name in VueUtils.apps[app_name]._data
                            }
                        })

                    @post(f"{app_url}/data/post")
                    def fn_get_data_from_vue():
                        req = request.json

                        for name, value in req["data"].items():
                            VueUtils.apps[app_name]._set_data(name, value)

                    @post(f"{app_url}/method")
                    def fn_call_vue_method():
                        req = request.json

                        VueUtils.apps[app_name]._call_method(req["method"])
                        return json_dumps({ "state": "success" })

                register_route_app(route_name, route_info["url"], route_info["components"])

            # elif route_name in VueUtils.components.keys():
            #     pass

        @get("/default_app")
        def redirect_to_first_app():
            redirect(route_options[list(VueUtils.apps.keys())[0]]["url"])

    @staticmethod
    def init(project_dir:str) -> Server:
        project_dir = os.path.abspath(project_dir)
        cur_cwd = os.getcwd()
        
        sys.path.append(project_dir)
        os.chdir(os.path.join(project_dir, "src"))

        # load components
        component_dir = os.path.join(project_dir, "src", "components")
        for component_name in [os.path.splitext(name)[0] for name in os.listdir(component_dir) if not name.startswith("__")]:
            importlib.import_module(f".{component_name}", "src.components")

        # load apps
        importlib.import_module(".main", "src")

        # set routes
        importlib.import_module(".router", "src")

        sys.path.remove(project_dir)
        os.chdir(cur_cwd)

        return Server(project_dir)
