# -*- coding: utf-8 -*-

class Binder():
    def __init__(self):
        self.__variables = []
        self.__methods = []
        self.__computes = []
        self.__events = {}

    @property
    def variables(self) -> list:
        return self.__variables

    @property
    def methods(self) -> list:
        return self.__methods

    @property
    def computes(self) -> list:
        return self.__computes

    @property
    def events(self) -> dict:
        return self.__events

    def variable(self, variable) -> bool:
        if not variable in self.__variables:
            self.__variables.append(variable)
            return True
        else:
            return False

    def method(self, func):
        def decorator(func):
            if not func.__name__ in self.__methods:
                self.__methods.append(func.__name__)

            return func

        return decorator(func)

    def compute(self, func):
        def decorator(func):
            if not func.__name__ in self.__computes:
                self.__computes.append(func.__name__)

            return func

        return decorator(func)

    def event(self, eventType:str):
        def decorator(func):
            self.__events[eventType] = func.__name__

            return func

        return decorator

class Model():
    binder = Binder()
    method = binder.method
    compute = binder.compute
    event = binder.event

    def __init__(self, webview = None):
        from copy import deepcopy

        self.__webview = webview

        excludeList = ["binder", "session", "method", "compute", "event", "name", "webview", "variables", "sessions", "computes", "methods", "events"]
        self.__mayVariables = [mname for mname in dir(self) if not mname in excludeList and not mname.startswith("__") and not mname.startswith("_Model__")]
        self.__sessions = {}
        for varName in self.__mayVariables:
            if varName.startswith("session_"):
                varNameVisible = varName[8:]
                exec("self.{0} = deepcopy(self.{1})".format(varNameVisible, varName))

                # self.__mayVariables.remove(varName)
                # self.__mayVariables.append(varNameVisible)

                self.__sessions[varNameVisible] = eval("self.{}".format(varNameVisible))

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def webview(self):
        return self.__webview

    @property
    def variables(self) -> dict:
        variableInfo = {}
        for varName in self.__mayVariables:
            if not varName in self.binder.computes and not varName in self.binder.methods and not varName in self.__sessions.keys() and not varName in self.binder.events.values():
                variableInfo[varName] = eval("self.{}".format(varName))

        return variableInfo

    @property
    def sessions(self) -> dict:
        return self.__sessions

    @property
    def computes(self) -> dict:
        computeInfo = {}
        for computeName in self.binder.computes:
            computeInfo[computeName] = eval("self.{}".format(computeName))

        return computeInfo

    @property
    def methods(self) -> dict:
        methodInfo = {}
        for methodName in self.binder.methods:
            methodInfo[methodName] = eval("self.{}".format(methodName))

        return methodInfo

    @property
    def events(self) -> dict:
        eventInfo = {}
        for eventType, eventName in self.binder.events.items():
            eventInfo[eventType] = eval("self.{}".format(eventName))

        return eventInfo

class View():
    def __init__(self, name:str, prefix:str, resourceText:str, styleText:str, scriptText:str, templateText:str, modelTextInfo:dict, webview = None):
        from .static import baseView

        self.__name = name
        self.__prefix = prefix

        self.__renderedText = baseView.replace(
            "{$viewName}", self.__name
        ).replace(
            "{$viewModels}", "\", \"".join(list(modelTextInfo.keys()))
        ).replace(
            "{$viewResource}", resourceText
        ).replace(
            "{$viewStyle}", styleText
        ).replace(
            "{$viewScript}", scriptText
        ).replace(
            "{$viewBody}", templateText
        )
        # if self.__prefix == "view":
        #     for line in self.__renderedText.split("\n"):
        #         if line.strip().startswith("<component ") and "name" in line:
        #             componentName = line[11:-1].split("=")[1][1:-1]

        #             self.__renderedText = self.__renderedText.replace(
        #                 line,
        #                 '<div style="width:100%;height:100%;"><object type="text/html" data="/components/{}" style="overflow:hidden;width:100%;height:100%;"></object></div>'.format(componentName)
        #             )

        self.__models = {}
        for modelName, modelText in modelTextInfo.items():
            exec(modelText)
            self.__models[modelName] = eval(modelName)(webview)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def prefix(self) -> str:
        return self.__prefix

    @property
    def models(self) -> dict:
        return self.__models

    def render(self, viewId:str) -> str:
        return self.__renderedText.replace("{$viewId}", viewId)
