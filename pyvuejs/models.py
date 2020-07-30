# -*- coding: utf-8 -*-
import types
from typing import Union
from inspect import signature
from threading import Thread

from .webview import Webwindow, WebDialog

class Model():
    __class_type__ = "model"
    app_view:Union[Webwindow, WebDialog] = None

    def __init__(self):
        self.__call_info = {}

        self.__variables, self.__events, self.__methods, self.__sessions = {}, {}, {}, {}
        for mname in dir(self):
            if not mname.startswith("__") and not mname.startswith("_Model__"):
                may_var = eval("self.{}".format(mname))
                if "__bind_info__" in dir(may_var):
                    bind_info = may_var.__bind_info__
                    
                    if bind_info["type"] == "variable":
                        self.__variables[mname] = may_var.value
                    elif bind_info["type"] == "session":
                        self.__sessions[mname] = may_var.value
                    elif bind_info["type"] == "method":
                        self.__methods[mname] = may_var
                    elif bind_info["type"] == "event":
                        self.__events[bind_info["name"]] = may_var

    def __set_variables(self):
        variable_names = list(self.__variables.keys())

        for v_name in variable_names:
            self.__variables[v_name] = eval("self.{}".format(v_name))

            if "__bind_info__" in dir(self.__variables[v_name]):
                self.__variables[v_name] = self.__variables[v_name].value

    @property
    def variables(self) -> dict:
        return self.__variables

    @property
    def sessions(self) -> dict:
        return self.__sessions

    @property
    def methods(self) -> dict:
        return self.__methods

    @property
    def events(self) -> dict:
        return self.__events

    def __call_function(self):
        if self.__call_info["call_type"] == "event":
            call = self.events[self.__call_info["call_name"]]
        else:
            call = self.methods[self.__call_info["call_name"]]

        call_params = signature(call).parameters
        if "session" in call_params.keys():
            call(self.__call_info["session"])
        else:
            call()

        self.__set_variables()

    def call_event(self, event_name:str, session = None):
        self.__call_info["call_type"] = "event"
        self.__call_info["call_name"] = event_name
        self.__call_info["session"] = session

        # thread = Thread(target = self.__call_function)
        # thread.start()
        self.__call_function()

    def call_method(self, method_name:str, session = None):
        self.__call_info["call_type"] = "method"
        self.__call_info["call_name"] = method_name
        self.__call_info["session"] = session

        # thread = Thread(target = self.__call_function)
        # thread.start()
        self.__call_function()

class View():
    def __init__(self, prefix:str, view_name:str, template:str, resources:str, style:str):
        self.__prefix = prefix
        self.__name = view_name
        self.__template = template
        self.__resources = resources
        self.__style = style

    @property
    def prefix(self) -> str:
        return self.__prefix

    @property
    def name(self) -> str:
        return self.__name

    def render(self, view_id:str, models:list) -> str:
        from .static import baseView

        return baseView.replace(
            "{$viewResource}", self.__resources
        ).replace(
            "{$viewStyle}", self.__style
        ).replace(
            "{$viewTemplate}", self.__template
        ).replace(
            "{$viewId}", view_id
        ).replace(
            "{$viewName}", self.name
        ).replace(
            "{$viewModels}", str(models)
        )
