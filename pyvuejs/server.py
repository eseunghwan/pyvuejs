# -*- coding: utf-8 -*-
from . import __path__
from .logger import Logger

class Server():
    def __init__(self, appDir:str):
        import os, sys, json
        from datetime import datetime
        from flask import Flask, request, jsonify
        from flask_socketio import SocketIO, emit

        # variables
        Logger.info("Prepare Server to run app...")
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
        self.__app.secret_key = "pyvuejsApp"
        self.__socketio = SocketIO(self.__app)

        # function routing points
        Logger.info("Setting function routing points...")
        @self.__app.before_first_request
        def onFirstRequest():
            pass

        @self.__app.route("/shutdown", methods = ["POST"])
        def onShutdown():
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

        # socket points
        Logger.info("Setting socket routing points...")
        @self.__socketio.on("feedbackPY", namespace = "/pyvuejsSocket")
        def onFeedback(res):
            print(res)

        @self.__socketio.on("initViewPY", namespace = "/pyvuejsSocket")
        def onInitView(res):
            # if res["id"] in self.__session["app"]["mpa"].keys():
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

        Logger.info("Routing points are ready!\n")

        self.__interpret_appDir()
        Logger.info("Server is ready!\n")

    def __interpret_appDir(self):
        import os, sys
        from glob import glob
        from importlib import import_module
        from flask import Blueprint, session
        from .models import View

        Logger.info("Interpreting app...")
        if os.path.exists(self.__appDir):
            sys.path.append(self.__appDir)

            Logger.info("Interpreting view files...")
            for pvPath in glob(os.path.join(self.__appDir, "views", "*.pvue")):
                pvInfo = self.__interpret_pyvue(pvPath)
                
                view:View = View(
                    pvInfo["name"], pvInfo["prefix"],
                    pvInfo["resource"], pvInfo["style"], pvInfo["script"],
                    pvInfo["template"],
                    pvInfo["model"]
                )

                if pvInfo["prefix"] == "view":
                    self.__session["app"]["views"][pvInfo["name"]] = view
                elif pvInfo["prefix"] == "component":
                    self.__session["app"]["components"][pvInfo["name"]] = view

                Logger.info("{}.pvue has been interpreted".format(pvInfo["name"]))
            Logger.info("Finished!\n")

            Logger.info("Linking static files to server...")
            staticDir = os.path.join(self.__appDir, "static")
            if os.path.exists(staticDir):
                self.__app.register_blueprint(
                    Blueprint(
                        os.path.basename(self.__appDir), "pyvue",
                        static_url_path = "/app",
                        static_folder = staticDir
                    )
                )
            Logger.info("Finished!\n")
        
        Logger.info("App has been ready!\n")

    def __interpret_pyvue(self, pvFile) -> dict:
        import os

        with open(pvFile, "r", encoding = "utf-8") as pvr:
            pvt = pvr.read()

            prefixLine = pvt.split("\n")[0]
            if prefixLine.startswith("!prefix"):
                prefix = prefixLine[8:]
            else:
                prefix = "view"

            pvInfo = {
                "resource": "",
                "style": "",
                "template": "",
                "script": "",
                "model": {}
            }
            for key in pvInfo.keys():
                try:
                    block = pvt.split("<{}>".format(key))[1].split("</{}>".format(key))[0]
                except IndexError:
                    block = ""

                if not block == "":
                    lines = block.split("\n")[1:-1]
                    if len(lines) > 0:
                        stripLength = len(lines[0][:-1 * len(lines[0].strip())])

                        blockStripLines = [
                            line[stripLength:]
                            for line in lines
                        ]

                        if key == "template":
                            if prefix == "view":
                                for idx in range(len(blockStripLines)):
                                    line = blockStripLines[idx]
                                    if line.strip().startswith("<component ") and "name" in line:
                                        componentName = line[11:-2].split("=")[1].strip()[1:-1]
                                        tabSpace = line.replace(line.strip(), "")

                                        blockStripLines[idx] = tabSpace + '<object type="text/html" data="/components/{}" style="overflow:hidden;width:100%;height:100%;"></object>'.format(componentName)

                            pvInfo[key] = "\n".join(blockStripLines)
                        elif key == "model":
                            lineNums = []
                            for idx in range(len(blockStripLines)):
                                line = blockStripLines[idx]
                                if line.startswith("Model ") and line.endswith(":"):
                                    lineNums.append(idx)
                                    blockStripLines[idx] = "class {}(Model):".format(line[6:-1])
                                elif line.strip().startswith("def ") and line.endswith(":"):
                                    blockStripLines[idx] = line.split("(self")[0] + "(self, session):"


                            for idx in range(len(lineNums)):
                                startNum = lineNums[idx]
                                if idx < len(lineNums) - 1:
                                    endNum = lineNums[idx + 1]
                                else:
                                    endNum = len(blockStripLines)

                                modelLines = blockStripLines[startNum:endNum]
                                if modelLines[-1] == "":
                                    modelLines.pop(-1)

                                for mlIdx in range(1, len(modelLines)):
                                    line = modelLines[mlIdx]
                                    if ":session" in line:
                                        varName = line.split(":session")[0].strip()
                                        modelLines[mlIdx] = line.replace(
                                            varName + ":session",
                                            "session_" + varName
                                        )

                                insertSpace = modelLines[1].replace(modelLines[1].strip(), "")
                                modelLines.insert(1, insertSpace + "binder = Binder()")
                                modelLines.insert(2, insertSpace + "method = binder.method")
                                modelLines.insert(3, insertSpace + "compute = binder.compute")
                                modelLines.insert(4, insertSpace + "event = binder.event")
                                modelLines.insert(5, "")

                                pvInfo[key][modelLines[0][6:-8]] = "\n".join(modelLines)
                        else:
                            pvInfo[key] = "\n".join(blockStripLines)

            pvInfo["name"] = os.path.splitext(os.path.basename(pvFile))[0]
            pvInfo["prefix"] = prefix

            return pvInfo

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

    def start(self, host:str = "0.0.0.0", port:int = 8000):
        import os
        from flask import request, session
        from copy import deepcopy

        @self.__app.route("/views/<viewName>")
        def showView(viewName):
            if viewName in self.__session["app"]["views"].keys():
                viewId = request.remote_addr
                if not viewId in self.__session["data"]["mpa"].keys():
                    self.__session["data"]["mpa"][viewId] = {}

                if not viewId in self.__session["app"]["mpa"].keys():
                    self.__session["app"]["mpa"][viewId] = {}

                if not viewName in self.__session["app"]["mpa"][viewId].keys():
                    self.__session["app"]["mpa"][viewId][viewName] = deepcopy(self.__session["app"]["views"][viewName])

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

        @self.__app.route("/components/<viewName>")
        def showComponent(viewName):
            if viewName in self.__session["app"]["components"].keys():
                viewId = request.remote_addr
                if not viewId in self.__session["data"]["mpa"].keys():
                    self.__session["data"]["mpa"][viewId] = {}

                if not viewId in self.__session["app"]["mpa"].keys():
                    self.__session["app"]["mpa"][viewId] = {}

                if not viewName in self.__session["app"]["mpa"][viewId].keys():
                    self.__session["app"]["mpa"][viewId][viewName] = deepcopy(self.__session["app"]["components"][viewName])

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

        try:
            if host in ("127.0.0.1", "localhost"):
                host = "0.0.0.0"

            Logger.info("Server started on \"{}:{}\"".format(host, port))
            Logger.info("Please check Devtool to show data transfers")
            self.__socketio.run(self.__app, host = host, port = port)
        except KeyboardInterrupt:
            os.remove(os.path.join(self.__appDir, ".state"))
