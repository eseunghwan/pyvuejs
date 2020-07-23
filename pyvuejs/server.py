# -*- coding: utf-8 -*-
# import modules
import os, sys, json, signal
from threading import Timer
from collections import OrderedDict
from datetime import datetime
from glob import glob
from copy import copy, deepcopy
import subprocess
from flask import Flask, Blueprint, redirect, request, jsonify
from flask_socketio import SocketIO, emit

from . import __path__
from .logger import Logger
from .models import View
from .webview import WebView
from .interpreting import interprete_appDir

class Server():
    def __init__(self, appDir:str, enableLogging:bool = True, webview:WebView = None):
        # check logging
        self.__logging = enableLogging

        # variables
        if self.__logging:
            Logger.info("Prepare Server to run app...")

        self.__webview = webview
        self.__appDir = os.path.abspath(appDir)
        self.__session = {
            "app": {
                "mpa": {},
                "views": {},
                "components": {},
                "updatedTime": {}
            },
            "data": {
                "mpa": {},
                "excludes": { "id": "", "name": "" }
            },
            "config": {
                "expiredTime": 1800
            }
        }

        self.__app = Flask(
            "pyvue",
            static_folder = os.path.join(__path__[0], "static"),
            template_folder = os.path.join(__path__[0], "static")
        )
        self.__app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1
        self.__app.secret_key = "pyvuejsApp"
        self.__socketio = SocketIO(self.__app)

        # view routing points
        if self.__logging:
            Logger.info("Setting view/component routing points...")

        @self.__app.after_request
        def add_header(response):
            response.headers["Cache-Control"] = "no-store"
            return response

        @self.__app.route("/views/<viewName>")
        def showView(viewName):
            if viewName in self.__session["app"]["views"].keys():
                viewId = request.remote_addr
                if not viewId in self.__session["data"]["mpa"].keys():
                    self.__session["data"]["mpa"][viewId] = {}

                if not viewId in self.__session["app"]["mpa"].keys():
                    self.__session["app"]["mpa"][viewId] = OrderedDict()

                if not viewName in self.__session["app"]["mpa"][viewId].keys():
                    try:
                        self.__session["app"]["mpa"][viewId][viewName] = deepcopy(self.__session["app"]["views"][viewName])
                    except TypeError as err:
                        if err.args[0].startswith("can't pickle"):
                            self.__session["app"]["mpa"][viewId][viewName] = copy(self.__session["app"]["views"][viewName])
                        else:
                            print(err.args)

                    for model in self.__session["app"]["mpa"][viewId][viewName].models.values():
                        for varName, var in model.sessions.items():
                            self.__session["data"]["mpa"][viewId][varName] = var

                        if "load" in model.events.keys():
                            model.events["load"](self.__session["data"]["mpa"][viewId])

                for model in self.__session["app"]["mpa"][viewId][viewName].models.values():
                    if "show" in model.events.keys():
                        model.events["show"](self.__session["data"]["mpa"][viewId])

                return self.__session["app"]["mpa"][viewId][viewName].render(viewId)
            else:
                viewNames = list(self.__session["app"]["views"].keys())
                if viewName == "def@ltWindowed" and len(viewNames) > 0:
                    if "main" in viewNames:
                        return redirect("/views/main")
                    else:
                        return redirect("/views/{}".format(viewNames[0]))
                else:
                    return ""

        @self.__app.route("/components/<viewName>")
        def showComponent(viewName):
            if viewName in self.__session["app"]["components"].keys():
                viewId = request.remote_addr
                if not viewId in self.__session["data"]["mpa"].keys():
                    self.__session["data"]["mpa"][viewId] = {}

                if not viewId in self.__session["app"]["mpa"].keys():
                    self.__session["app"]["mpa"][viewId] = OrderedDict()

                if not viewName in self.__session["app"]["mpa"][viewId].keys():
                    try:
                        self.__session["app"]["mpa"][viewId][viewName] = deepcopy(self.__session["app"]["components"][viewName])
                    except TypeError as err:
                        if err.args[0].startswith("can't pickle"):
                            self.__session["app"]["mpa"][viewId][viewName] = copy(self.__session["app"]["components"][viewName])
                        else:
                            print(err.args)

                    for model in self.__session["app"]["mpa"][viewId][viewName].models.values():
                        for varName, var in model.sessions.items():
                            self.__session["data"]["mpa"][viewId][varName] = var

                        if "load" in model.events.keys():
                            model.events["load"](self.__session["data"]["mpa"][viewId])

                for model in self.__session["app"]["mpa"][viewId][viewName].models.values():
                    if "show" in model.events.keys():
                        model.events["show"](self.__session["data"]["mpa"][viewId])

                return self.__session["app"]["mpa"][viewId][viewName].render(viewId)
            else:
                return ""

        # function routing points
        if self.__logging:
            Logger.info("Setting function routing points...")

        @self.__app.before_first_request
        def onFirstRequest():
            pass

        @self.__app.route("/shutdown", methods = ["POST"])
        def onShutdown():
            if self.__logging:
                Logger.info("App is shutting down...")

            sys.exit()

        @self.__app.route("/session/upload", methods = ["POST"])
        def onSessionUpload():
            res = json.loads(request.data)

            self.__session["data"]["mpa"][res["id"]] = res["session"]
            self.__session["data"]["excludes"]["id"] = res["id"]
            self.__session["data"]["excludes"]["name"] = res["name"]
            self.__session["app"]["updatedTime"][res["id"]] = datetime.now()

            return jsonify({
                "state": "success"
            })

        @self.__app.route("/session/download", methods = ["POST"])
        def onSessionDownload():
            res = json.loads(request.data)

            try:
                # check expiredTime
                for viewId, updateTime in self.__session["app"]["updatedTime"].items():
                    if not res["id"] == viewId:
                        if (datetime.now() - updateTime).total_seconds() >= self.__session["config"]["expiredTime"]:
                            self.__session["app"]["mpa"].pop(viewId)
                            self.__session["data"]["mpa"].pop(viewId)

                resp = {
                    "id": self.__session["data"]["excludes"]["id"],
                    "excludeName": self.__session["data"]["excludes"]["name"],
                    "sessions": {}
                }
                for view in self.__session["app"]["mpa"][resp["id"]].values():
                    sessionSet = {}
                    for modelName in view.models.keys():
                        sessionSet[modelName] = self.__session["data"]["mpa"][resp["id"]]

                    resp["sessions"][view.name] = sessionSet

                return jsonify(resp)
            except KeyError:
                return jsonify({
                    "id": "",
                    "excludeName": "",
                    "sessions": {}
                })

        # socket points
        if self.__logging:
            Logger.info("Setting socket routing points...")

        @self.__socketio.on("feedbackPY", namespace = "/pyvuejsSocket")
        def onFeedback(res):
            print(res)

        @self.__socketio.on("initViewPY", namespace = "/pyvuejsSocket")
        def onInitView(res):
            if res["id"] in self.__session["app"]["mpa"].keys():
                view = self.__session["app"]["mpa"][res["id"]][res["name"]]
                emit("initViewJS", {
                    "id": res["id"],
                    "name": res["name"],
                    "session": self.__session["data"]["mpa"][res["id"]],
                    "data": {
                        modelName: model.variables
                        for modelName, model in view.models.items()
                    },
                    "computes": {
                        modelName: list(model.computes.keys())
                        for modelName, model in view.models.items()
                    },
                    "methods": {
                        modelName: list(model.methods.keys())
                        for modelName, model in view.models.items()
                    }
                })

        @self.__socketio.on("compute", namespace = "/pyvuejsSocket")
        def onCompute(res):
            model = self.__session["app"]["mpa"][res["id"]][res["name"]].models[res["model"]]

            for varName, value in res["variables"].items():
                exec("model.{} = value".format(varName))

            self.__session["data"]["mpa"][res["id"]] = res["session"]
            model.computes[res["method"]](self.__session["data"]["mpa"][res["id"]])
            
            emit("update", {
                "id": res["id"],
                "name": res["name"],
                "model": model.name,
                "variables": model.variables,
                "session": self.__session["data"]["mpa"][res["id"]]
            })

        @self.__socketio.on("method", namespace = "/pyvuejsSocket")
        def onMethod(res):
            model = self.__session["app"]["mpa"][res["id"]][res["name"]].models[res["model"]]

            for varName, value in res["variables"].items():
                exec("model.{} = value".format(varName))

            self.__session["data"]["mpa"][res["id"]] = res["session"]
            model.methods[res["method"]](self.__session["data"]["mpa"][res["id"]])
            
            emit("update", {
                "id": res["id"],
                "name": res["name"],
                "model": model.name,
                "variables": model.variables,
                "session": self.__session["data"]["mpa"][res["id"]]
            })

        if self.__logging:
            Logger.info("Routing points are ready!\n")

        interprete_appDir(self.__appDir, self.__app, self.__session["app"], webview, self.__logging)
        if self.__logging:
            Logger.info("Server is ready!\n")

    def __get_view_type(self, name:str) -> str:
        if name in self.__session["app"]["views"].keys():
            return "view"
        elif name in self.__session["app"]["components"].keys():
            return "component"

    def __create_viewFunc(self, fName, view):
        return """
def {0}():
    return '''
{1}
'''
""".format(fName, view.render())

    def start(self, host:str = "0.0.0.0", port:int = 8080):
        try:
            if host in ("127.0.0.1", "localhost"):
                host = "0.0.0.0"

            if self.__logging:
                Logger.info("Server started on \"http://{}:{}\"".format(
                    "127.0.0.1" if host == "0.0.0.0" else host,
                    port
                ))
                Logger.info("Please check Devtool to show data transfers")
            self.__socketio.run(self.__app, host = host, port = port)
        except KeyboardInterrupt:
            os.remove(os.path.join(self.__appDir, ".state"))

class WindowedServer():
    def __init__(self, enableLogging:bool = True):
        self.__logging = enableLogging

    def __appview_show(self):
        if self.__logging:
            Logger.info("Webview is ready!")

    def __appview_closed(self):
        if self.__logging:
            Logger.info("Shutting down background server...")

        subprocess.Popen([sys.executable, ".\manage.py", "stop"])
        os.kill(os.getpid(), signal.SIGTERM)

    def __start_server_background(self, appDir:str, port:int):
        Server(appDir, False, self.__appView).start("127.0.0.1", port)

    def start(self, appDir:str, port:int = 8080, window_size:list = [900, 600]):
        from pycefsharp.cef import CefApp

        if self.__logging:
            Logger.info("Setting up webview...")

        appIcon = os.path.join(appDir, "static", "favicon.ico")
        if not os.path.exists(appIcon):
            appIcon = os.path.join(__path__[0], "static", "favicon.ico")

        # self.__qtApp.setWindowIcon(QIcon(appIcon))
        self.__appView = WebView(
            "http://127.0.0.1:{}/views/def@ltWindowed".format(port),
            os.path.basename(appDir),
            appIcon,
            (-1, -1, window_size[0], window_size[1])
        )
        self.__appView._cef_form.IsMdiContainer = True
        self.__appView.on_show = self.__appview_show
        self.__appView.on_close = self.__appview_closed

        if self.__logging:
            Logger.info("Start server on background...")

        os.chdir(appDir)
        self.__timer = Timer(1, self.__start_server_background, (appDir, port))
        self.__timer.start()

        CefApp().Run(self.__appView)
