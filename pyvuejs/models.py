# -*- coding: utf-8 -*-

class Variable():
    def __init__(self, value):
        self.__value = value
        self.__compute = None
        self.__method = None

    def __repr__(self):
        return repr(self.__value)

    def __str__(self):
        return str(self.__value)

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, newValue):
        if isinstance(newValue, Variable):
            newValue = newValue.value

        self.__value = newValue

    @property
    def value(self):
        return self.__value

    @property
    def compute(self):
        return self.__compute

    @property
    def method(self):
        return self.__method

    def __add__(self, other):
        if isinstance(other, Variable):
            other = other.value

        self.__value = self.__value + other
        return self

    def __sub__(self, other):
        if isinstance(other, Variable):
            other = other.value

        self.__value = self.__value - other
        return self

    def __mul__(self, other):
        if isinstance(other, Variable):
            other = other.value

        self.__value = self.__value * other
        return self

    def __truediv__(self, other):
        if isinstance(other, Variable):
            other = other.value

        self.__value = self.__value / other
        return self

    def __floordiv__(self, other):
        if isinstance(other, Variable):
            other = other.value

        self.__value = self.__value // other
        return self

    def __eq__(self, other):
        if isinstance(other, Variable):
            other = other.value

        return self.__value == other

    def connect(self, mType):
        def decorator(method):
            if mType == "compute":
                self.__compute = method
            else:
                self.__method = method

            return method

        return decorator

class Model():
    def __init__(self):
        self.__variableNames = []
        for mname in [mname for mname in dir(self) if not mname in ("name", "variables")]:
            if isinstance(eval("self.{}".format(mname)), Variable):
                self.__variableNames.append(mname)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def variables(self) -> dict:
        variableInfo = {}
        for varName in self.__variableNames:
            variableInfo[varName] = eval("self.{}".format(varName))

        return variableInfo

    @property
    def computes(self) -> dict:
        computeInfo = {}
        for varName in self.__variableNames:
            compute = eval("self.{}".format(varName)).compute
            
            if not compute == None:
                computeInfo[compute.__name__] = compute

        return computeInfo

    @property
    def methods(self) -> dict:
        methodInfo = {}
        for varName in self.__variableNames:
            method = eval("self.{}".format(varName)).method
            
            if not method == None:
                methodInfo[method.__name__] = method

        return methodInfo

class View():
    def __init__(self, name:str, prefix:str, resourceText:str, styleText:str, scriptText:str, templateText:str, modelTextInfo:dict):
        from lxml.html import fromstring, tostring
        from .static import baseView, baseComponent

        self.__name = name
        self.__prefix = prefix

        # self.__renderedText = eval("base{}".format(prefix.capitalize())).replace(
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

        self.__models = {}
        for modelName, modelText in modelTextInfo.items():
            exec(modelText)
            self.__models[modelName] = eval(modelName + "()")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def prefix(self) -> str:
        return self.__prefix

    @property
    def models(self) -> dict:
        return self.__models

    def render(self) -> str:
        if self.__prefix == "view":
            for line in self.__renderedText.split("\n"):
                if line.strip().startswith("<component ") and "name" in line:
                    componentName = line[11:-1].split("=")[1][1:-1]

                    self.__renderedText = self.__renderedText.replace(
                        line,
                        '<div style="width:100%;height:100%;"><object type="text/html" data="/components/{}" style="overflow:hidden;"></object></div>'.format(componentName)
                    )

        return self.__renderedText
