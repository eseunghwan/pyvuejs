# -*- coding: utf-8 -*-
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide2.QtCore import QUrl, Signal
from PySide2.QtGui import QIcon


__qtApp = QApplication(sys.argv)
__main_window = None
class WebDialog(QDialog):
    def __init__(self, title:str, url:str, x:int = None, y:int = None, width:int = None, height:int = None, parent = None):
        super().__init__(parent)

        self.__central_layout = QGridLayout(self)
        self.__central_layout.setContentsMargins(0, 0, 0, 0)

        self.__webview = QWebEngineView(self)
        self.__webview.setPage(QWebEnginePage(parent = self.__webview))
        self.__webview.page().loadFinished.connect(self.__onload)
        self.__central_layout.addWidget(self.__webview, 0, 0, 1, 1)

        self.setWindowTitle(title)
        self.hide()
        
        if not x == None and not y == None:
            self.move(x, y)
        else:
            resolution = QApplication.desktop().screenGeometry()
            self.move(
                int((resolution.width() - self.width()) / 2),
                int((resolution.height() - self.height()) / 2)
            )
        
        self.resize(
            950 if width == None else width,
            650 if height == None else height
        )

        self.__webview.setUrl(QUrl(url))

    def __onload(self, ev):
        self.open()

class Webwindow(QMainWindow):
    create_window = Signal(object, str, str, int, int, int, int)
    create_dialog = Signal(object, str, str, int, int, int, int, QMainWindow)

    def __init__(self, title:str, url:str, x:int = None, y:int = None, width:int = None, height:int = None):
        super().__init__(None)
        self.create_window.connect(self.on_create_window)
        self.create_dialog.connect(self.on_create_dialog)

        self.__subwindows = []

        self.__webview = QWebEngineView(self)
        self.__webview.setPage(QWebEnginePage(parent = self.__webview))
        self.__webview.page().loadFinished.connect(self.__onload)
        self.setCentralWidget(self.__webview)

        self.setWindowTitle(title)
        self.hide()
        
        if not x == None and not y == None:
            self.move(x, y)
        else:
            resolution = QApplication.desktop().screenGeometry()
            self.move(
                int((resolution.width() - self.width()) / 2),
                int((resolution.height() - self.height()) / 2)
            )
        
        self.resize(
            950 if width == None else width,
            650 if height == None else height
        )

        self.__webview.setUrl(QUrl(url))

    def __onload(self, ev):
        self.showNormal()

    def on_create_window(self, func, title:str, url:str, x:int, y:int, width:int, height:int) -> QMainWindow:
        win = func(title, url, x, y, width, height)
        self.__subwindows.append(win)

        return win

    def on_create_dialog(self, func, title:str, url:str, x:int, y:int, width:int, height:int, parent) -> WebDialog:
        dlg = func(title, url, x, y, width, height, self if parent == None else parent)
        self.__subwindows.append(dlg)

        return dlg

def create_window(title:str, url:str, x:int = None, y:int = None, width:int = None, height:int = None):
    global __main_window

    def _create_window(title, url, x, y, width, height):
        return Webwindow(title, url, x, y, width, height)

    if __main_window == None:
        __main_window = Webwindow(title, url, x, y, width, height)
        win = __main_window
    else:
        win = __main_window.create_dialog.emit(_create_window, title, url, x, y, width, height)

    return win

def create_dialog(title:str, url:str, x:int = None, y:int = None, width:int = None, height:int = None, parent:Webwindow = None):
    global __main_window

    def _create_dialog(title, url, x, y, width, height, parent):
        return WebDialog(title, url, x, y, width, height, parent)

    if __main_window == None:
        raise RuntimeError("Please create main Webwindow first!")
    else:
        return __main_window.create_dialog.emit(_create_dialog, title, url, x, y, width, height, parent)

def start(app_icon:str):
    global __qtApp

    __qtApp.setWindowIcon(QIcon(app_icon))
    __qtApp.exec_()
