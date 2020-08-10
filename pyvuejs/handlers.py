# -*- coding: utf-8 -*-

class VueException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class LoadingException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
