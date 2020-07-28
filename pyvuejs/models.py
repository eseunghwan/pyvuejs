# -*- coding: utf-8 -*-
import types
from inspect import signature
from pycefsharp.cef import CefView

class Model():
    __class_type__ = "model"
    webview:CefView = None

    def __init__(self):
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

    def call_event(self, event_name:str, session = None):
        event = self.events[event_name]
        event_params = signature(event).parameters
        if "session" in event_params.keys():
            event(session)
        else:
            event()

    def call_method(self, method_name:str, session = None):
        method = self.methods[method_name]
        method_params = signature(method).parameters.keys()
        if "session" in method_params or "session_data" in method_params:
            method(session)
        else:
            method()

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
