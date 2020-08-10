# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from ..static import view_template
from ..handlers import VueException


class VueComponent():
    name:str = ""
    props:list = []
    template:str = ""
    style:str = ""
    # methods:dict = {}

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
    @staticmethod
    def createApp(app_class) -> VueModel:
        try:
            cls = app_class()
        except:
            cls = app_class

        app = VueModel()

        if hasattr(cls, "data"):
            setattr(app, "data", getattr(cls, "data"))

        if hasattr(cls, "methods"):
            setattr(app, "methods", getattr(cls, "methods"))

        if hasattr(cls, "created"):
            setattr(app, "created", getattr(cls, "created"))

        if hasattr(cls, "mounted"):
            setattr(app, "mounted", getattr(cls, "mounted"))

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

        setattr(component, "name", name)

        if hasattr(cls, "props"):
            setattr(component, "props", getattr(cls, "props"))

        if hasattr(cls, "template"):
            setattr(component, "template", getattr(cls, "template"))

        if hasattr(cls, "style"):
            setattr(component, "style", getattr(cls, "style"))

        # if hasattr(cls, "methods"):
        #     setattr(component, "methods", getattr(cls, "methods")())

        return component

class VueInstance():
    def __init__(self, vue_file:str, vue_model:VueModel, app_config:dict):
        self.__vue = os.path.abspath(vue_file)
        self.__model = vue_model
        self.__app_config = app_config

        self.__model.created()

    @property
    def _data(self) -> dict:
        return {
            name: self.get_data(name)
            for name in self.__model._data.keys()
        }

    @property
    def _methods(self) -> list:
        return list(self.__model._methods.keys())

    def get_data(self, name:str):
        if name in self.__model._data.keys():
            return getattr(self.__model, name)
            # return eval("self.__model.{}".format(name))

    def set_data(self, name:str, value):
        if name in self.__model._data.keys():
            setattr(self.__model, name, value)
            # exec("self.__model.{} = value".format(name))

    def get_method(self, name:str):
        if name in self.__model._methods.keys():
            return getattr(self.__model, name)
            # return eval("self.__model.{}".format(name))

    def call_method(self, name:str):
        self.get_method(name)(self.__model)

    def __parse_vue(self) -> dict:
        block_info = {}

        with open(self.__vue, "r", encoding = "utf-8") as vue_read:
            vue_text = vue_read.read()

            for block_name in ("template", "style"):
                block_start, block_end = "<{}>".format(block_name), "</{}>".format(block_name)

                if block_start in vue_text and block_end in vue_text:
                    block_info[block_name] = vue_text.split(block_start)[1].split(block_end)[0]

        return block_info

    def render(self) -> str:
        vue_info = self.__parse_vue()
        self.__model.mounted()

        return view_template.replace(
            "{$selector}", self.__model.selector
        ).replace(
            "{$template}", vue_info["template"]
        ).replace(
            "{$style}", vue_info["style"]
        ).replace(
            "{$app_url}", self.__app_config["url"]
        ).replace(
            "{$title}", self.__app_config["title"]
        ).replace(
            "{$app_url}", self.__app_config["url"]
        )
