# -*- coding: utf-8 -*-

class Variable():
    def __init__(self, value):
        self.__value = value
        # self.__name = self.__class__.__name__

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

    # @property
    # def name(self) -> str:
    #     return self.__name

    # @name.setter
    # def name(self, newName:str):
    #     self.__name = newName

    @property
    def value(self):
        return self.__value

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

    # def compute(self):
    #     pass

class Model():
    def __init__(self):
        self.__variables = {}

        for mname in dir(self):
            if isinstance(eval("self.{}".format(mname)), Variable):
                self.__variables[mname] = eval("self.{}".format(mname))

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def variables(self) -> dict:
        return self.__variables

class View():
    def __init__(self, name:str, styleText:str, scriptText:str, templateText:str, modelTextInfo:dict):
        from lxml.html import fromstring, tostring
        from .static import baseView

        self.__name = name
        self.__renderedText = baseView.replace(
            "{$viewName}", self.__name
        ).replace(
            "{$viewModels}", "\", \"".join(list(modelTextInfo.keys()))
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
    def models(self) -> dict:
        return self.__models

    def render(self) -> str:
        return self.__renderedText
