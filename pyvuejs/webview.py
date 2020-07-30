# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide2.QtCore import QUrl, Signal
from PySide2.QtGui import QIcon


qtApp = QApplication(sys.argv)
windows = OrderedDict()
dialogs = OrderedDict()
current_window = None
current_dialog = None


class WebDialog(QDialog):
    def __init__(self, title:str, url:str, name:str = None, x:int = None, y:int = None, width:int = None, height:int = None, parent = None):
        super().__init__(parent)

        global qtApp, dialogs
        if name in ("", None):
            self.__name = "dialog{}".format(len(dialogs.keys()))
        else:
            self.__name = name

        self.__central_layout = QGridLayout(self)
        self.__central_layout.setContentsMargins(0, 0, 0, 0)

        self.__webview = QWebEngineView(self)
        self.__webview.setPage(QWebEnginePage(parent = self.__webview))
        self.__webview.page().loadFinished.connect(self.__onload)
        self.__central_layout.addWidget(self.__webview, 0, 0, 1, 1)

        self.setWindowTitle(title)
        self.hide()
        
        self.resize(
            950 if width in (-1, None) else width,
            650 if height in (-1, None) else height
        )

        if not x in (-1, None) and not y in (-1, None):
            self.move(x, y)
        else:
            resolution = qtApp.desktop().screenGeometry()
            self.move(
                int((resolution.width() - self.width()) / 2),
                int((resolution.height() - self.height()) / 2)
            )

        self.__webview.page().setUrl(QUrl(url))

    @property
    def name(self) -> str:
        return self.__name

    def __onload(self, ev):
        self.open()

class Webwindow(QMainWindow):
    create_window = Signal(object, str, str, str, int, int, int, int)
    create_dialog = Signal(object, str, str, str, int, int, int, int, QMainWindow)

    def __init__(self, title:str, url:str, name:str = None, x:int = None, y:int = None, width:int = None, height:int = None):
        super().__init__(None)
        self.create_window.connect(self.__on_create_window)
        self.create_dialog.connect(self.__on_create_dialog)

        global qtApp, windows
        if name in ("", None):
            self.__name = "window{}".format(len(windows.keys()))
        else:
            self.__name = name

        self.__webview = QWebEngineView(self)
        self.__webview.setPage(QWebEnginePage(parent = self.__webview))
        self.__webview.page().loadFinished.connect(self.__onload)
        self.setCentralWidget(self.__webview)

        self.setWindowTitle(title)
        self.hide()
        
        self.resize(
            950 if width in (-1, None) else width,
            650 if height in (-1, None) else height
        )

        if not x in (-1, None) and not y in (-1, None):
            self.move(x, y)
        else:
            resolution = qtApp.desktop().screenGeometry()
            self.move(
                int((resolution.width() - self.width()) / 2),
                int((resolution.height() - self.height()) / 2)
            )

        self.__webview.page().setUrl(QUrl(url))

    @property
    def name(self) -> str:
        return self.__name

    def __onload(self, ev):
        self.showNormal()

    def __on_create_window(self, func, title:str, name:str, url:str, x:int, y:int, width:int, height:int) -> QMainWindow:
        global windows, current_window

        current_window = func(title, url, name, x, y, width, height)
        windows[current_window.name] = current_window

    def __on_create_dialog(self, func, title:str, url:str, name:str, x:int, y:int, width:int, height:int, parent) -> WebDialog:
        global dialogs, current_dialog

        current_dialog = func(title, url, name, x, y, width, height, self if parent == None else parent)
        dialogs[current_dialog.name] = current_dialog

def create_window(title:str, url:str, name:str = None, x:int = None, y:int = None, width:int = None, height:int = None):
    global windows, current_window

    def _create_window(title, url, name, x, y, width, height):
        return Webwindow(title, url, name, x, y, width, height)

    if not "main" in windows.keys():
        windows["main"] = Webwindow(title, url, "main", x, y, width, height)
        return windows["main"]
    else:
        current_window = None
        res = windows["main"].create_window.emit(_create_window, title, url, name,
            -1 if x == None else x, -1 if y == None else y,
            -1 if width == None else width, -1 if height == None else height
        )
        while current_window == None:
            pass

        return current_window

def create_dialog(title:str, url:str, name:str = None, x:int = None, y:int = None, width:int = None, height:int = None, parent:Webwindow = None):
    global windows, dialogs, current_dialog

    def _create_dialog(title, url, name, x, y, width, height, parent):
        return WebDialog(title, url, name, x, y, width, height, parent)

    if not "main" in windows.keys():
        raise RuntimeError("Please create main Webwindow first!")
    else:
        res = windows["main"].create_dialog.emit(_create_dialog, title, url, name,
            -1 if x == None else x, -1 if y == None else y,
            -1 if width == None else width, -1 if height == None else height,
            parent
        )
        if res:
            while current_dialog == None:
                pass

            return current_dialog

def start(app_icon:str):
    qtApp.setWindowIcon(QIcon(app_icon))
    qtApp.exec_()
