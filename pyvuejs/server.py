# -*- coding: utf-8 -*-
from . import __path__

class Server():
    def __init__(self, appDir:str):
        import os, json
        from flask import Flask, request, jsonify
        from flask_socketio import SocketIO, emit

        self.__appSession = {}
        self.__dataSession = {}
        self.__dataSessionExcludes = {
            "id": "",
            "name": ""
        }
        self.__views = {}
        self.__components = {}
        self.__app = Flask(
            "pyvue",
            static_folder = os.path.join(__path__[0], "static"),
            template_folder = os.path.join(__path__[0], "static")
        )
        self.__app.secret_key = "pyvuejsApp"
        self.__socketio = SocketIO(self.__app)

        @self.__socketio.on("connect", namespace = "/pyvuejsSocket")
        def onConnect():
            emit("feedbackJS", {
                "job": "connect",
                "state": "success"
            })

        @self.__socketio.on("disconnect", namespace = "/pyvuejsSocket")
        def onDisconnect():
            emit("feedbackJS", {
                "job": "disconnect",
                "state": "success"
            })

        @self.__socketio.on("feedbackPY", namespace = "/pyvuejsSocket")
        def onFeedback(res):
            print(res)

        @self.__socketio.on("initViewPY", namespace = "/pyvuejsSocket")
        def onInitView(res):
            # if res["id"] in self.__appSession.keys():
            view = self.__appSession[res["id"]][res["name"]]
            emit("initViewJS", {
                "id": res["id"],
                "name": res["name"],
                "session": self.__dataSession[res["id"]],
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
            model = self.__appSession[res["id"]][res["name"]].models[res["model"]]

            for varName, value in res["variables"].items():
                exec("model.{} = value".format(varName))

            self.__dataSession[res["id"]] = res["session"]
            model.computes[res["method"]](self.__dataSession[res["id"]])
            
            emit("update", {
                "id": res["id"],
                "name": res["name"],
                "model": model.name,
                "variables": model.variables,
                "session": self.__dataSession[res["id"]]
            })

        @self.__socketio.on("method", namespace = "/pyvuejsSocket")
        def onMethod(res):
            model = self.__appSession[res["id"]][res["name"]].models[res["model"]]

            for varName, value in res["variables"].items():
                exec("model.{} = value".format(varName))

            self.__dataSession[res["id"]] = res["session"]
            model.methods[res["method"]](self.__dataSession[res["id"]])
            
            emit("update", {
                "id": res["id"],
                "name": res["name"],
                "model": model.name,
                "variables": model.variables,
                "session": self.__dataSession[res["id"]]
            })

        @self.__app.route("/session/upload", methods = ["POST"])
        def onSessionUpload():
            res = json.loads(request.data)

            self.__dataSession[res["id"]] = res["session"]
            self.__dataSessionExcludes["id"] = res["id"]
            self.__dataSessionExcludes["name"] = res["name"]

            return ""

        @self.__app.route("/session/download", methods = ["POST"])
        def onSessionDownload():
            resp = {
                "id": self.__dataSessionExcludes["id"],
                "excludeName": self.__dataSessionExcludes["name"],
                "sessions": {}
            }
            for viewId, session in self.__dataSession.items():
                sessionSet = {}
                for view in self.__appSession[viewId].values():
                    sessionSet[view.name] = {}
                    for modelName in view.models.keys():
                        sessionSet[view.name][modelName] = session

                resp["sessions"][viewId] = sessionSet

            return jsonify(resp)

        self.__init_appDir(appDir)

    def __init_appDir(self, appDirPath:str):
        import os, sys
        from glob import glob
        from importlib import import_module
        from flask import Blueprint
        from .models import View

        appDirPath = os.path.abspath(appDirPath)
        if os.path.exists(appDirPath):
            sys.path.append(appDirPath)
            for pvPath in glob(os.path.join(appDirPath, "views", "*.pvue")):
                pvInfo = self.__parse_pyvue(pvPath)
                
                view:View = View(
                    pvInfo["name"], pvInfo["prefix"],
                    pvInfo["resource"], pvInfo["style"], pvInfo["script"],
                    pvInfo["template"],
                    pvInfo["model"]
                )

                if pvInfo["prefix"] == "view":
                    self.__views[pvInfo["name"]] = view
                elif pvInfo["prefix"] == "component":
                    self.__components[pvInfo["name"]] = view

            dirList = os.listdir(appDirPath)
            if "static" in dirList:
                self.__app.register_blueprint(
                    Blueprint(
                        os.path.basename(appDirPath), "pyvue",
                        static_url_path = "/app",
                        static_folder = os.path.join(appDirPath, "static")
                    )
                )

    def __parse_pyvue(self, pvFile) -> dict:
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
        if name in self.__views.keys():
            return "view"
        elif name in self.__components.keys():
            return "component"

    # async def __send_ws(self, sendInfo:dict):
    #     import json

    #     try:
    #         await self.__websocket.send(json.dumps(sendInfo))
    #     except:
    #         print(sendInfo)

    # async def __get_ws(self) -> dict:
    #     import asyncio, json

    #     try:
    #         res:dict = json.loads(await self.__websocket.receive())
    #         if not "state" in res.keys():
    #             res["state"] = "success"
    #     except json.decoder.JSONDecodeError:
    #         res = {
    #             "job": "error",
    #             "state": "failed"
    #         }

    #     return res

    def __create_viewFunc(self, fName, view):
        return """
def {0}():
    return '''
{1}
'''
""".format(fName, view.render())

    def start(self, host:str = "0.0.0.0", port:int = 8000):
        import os
        from flask import request
        from copy import deepcopy

        @self.__app.route("/views/<viewName>")
        def showView(viewName):
            if viewName in self.__views.keys():
                viewId = request.remote_addr
                if not viewId in self.__dataSession.keys():
                    self.__dataSession[viewId] = {}

                if not viewId in self.__appSession.keys():
                    self.__appSession[viewId] = {}

                if not viewName in self.__appSession[viewId].keys():
                    self.__appSession[viewId][viewName] = deepcopy(self.__views[viewName])

                    for model in self.__appSession[viewId][viewName].models.values():
                        for varName, var in model.sessions.items():
                            self.__dataSession[viewId][varName] = var

                        if "load" in model.events.keys():
                            model.events["load"](self.__dataSession[viewId])

                for model in self.__appSession[viewId][viewName].models.values():
                    if "show" in model.events.keys():
                        model.events["show"](self.__dataSession[viewId])

                return self.__appSession[viewId][viewName].render(viewId)
            else:
                return ""

        @self.__app.route("/components/<viewName>")
        def showComponent(viewName):
            if viewName in self.__components.keys():
                viewId = request.remote_addr
                if not viewId in self.__dataSession.keys():
                    self.__dataSession[viewId] = {}

                if not viewId in self.__appSession.keys():
                    self.__appSession[viewId] = {}

                if not viewName in self.__appSession[viewId].keys():
                    self.__appSession[viewId][viewName] = deepcopy(self.__components[viewName])

                    for model in self.__appSession[viewId][viewName].models.values():
                        for varName, var in model.sessions.items():
                            self.__dataSession[viewId][varName] = var

                        if "load" in model.events.keys():
                            model.events["load"](self.__dataSession[viewId])

                for model in self.__appSession[viewId][viewName].models.values():
                    if "show" in model.events.keys():
                        model.events["show"](self.__dataSession[viewId])

                return self.__appSession[viewId][viewName].render(viewId)
            else:
                return ""

        try:
            self.__socketio.run(self.__app, host = "0.0.0.0", port = port)
        except KeyboardInterrupt:
            pass
