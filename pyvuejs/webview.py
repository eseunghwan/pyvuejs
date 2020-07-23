# -*- coding: utf-8 -*-
from pycefsharp.cef import CefView
from .logger import Logger

class WebView(CefView):
    def __init__(self, url:str, title:str, icon:str = None, geometry:list = [-1, -1, -1, -1], parent = None):
        super().__init__(url, title, icon, geometry)
