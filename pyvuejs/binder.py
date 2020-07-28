# -*- coding: utf-8 -*-

# def model(view_name:str):
#     def decorator(cls):
#         return cls

#     return decorator

class model_variable():
    __bind_info__ = { "type": "variable" }
    def __init__(self, raw_var):
        self.__raw_var = raw_var

    @property
    def value(self):
        return self.__raw_var

class session_variable():
    __bind_info__ = { "type": "session" }
    def __init__(self, raw_var):
        self.__raw_var = raw_var

    @property
    def value(self):
        return self.__raw_var

def method(func):
    def decorator(func):
        func.__bind_info__ = { "type": "method" }
        return func

    return decorator(func)

def event(event_name:str):
    def decorator(func):
        func.__bind_info__ = { "type": "event", "name": event_name }
        return func

    return decorator
