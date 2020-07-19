# -*- coding: utf-8 -*-
from . import __path__

class Server():
    def __init__(self, appDir:str):
        import os, string, json
        from quart import Quart, websocket
        from copy import deepcopy

        self.__appSession = {}
        self.__dataSession = {}
        self.__views = {}
        self.__components = {}
        self.__app = Quart(
            "pyvue",
            static_folder = os.path.join(__path__[0], "static"),
            template_folder = os.path.join(__path__[0], "static")
        )
        self.__websocket = websocket

        @self.__app.websocket("/ws")
        async def ws():
            while True:
                res = await self.__get_ws()

                if res["state"] == "success":
                    if res["job"] == "open":
                        if not res["id"] in self.__appSession.keys():
                            self.__appSession[res["id"]] = {}

                        if not res["id"] in self.__dataSession.keys():
                            self.__dataSession[res["id"]] = {}

                        if self.__get_view_type(res["name"]) == "view":
                            self.__appSession[res["id"]][res["name"]] = deepcopy(self.__views[res["name"]])
                        elif self.__get_view_type(res["name"]) == "component":
                            self.__appSession[res["id"]][res["name"]] = deepcopy(self.__components[res["name"]])

                        await self.__send_ws(
                            {
                                "job": "init",
                                "state": "success",
                                "id": res["id"],
                                "data": {
                                    modelName: {
                                        vName: var.value
                                        for vName, var in model.variables.items()
                                    }
                                    for modelName, model in self.__appSession[res["id"]][res["name"]].models.items()
                                },
                                "computes": {
                                    modelName: list(model.computes.keys())
                                    for modelName, model in self.__appSession[res["id"]][res["name"]].models.items()
                                },
                                "methods": {
                                    modelName: list(model.methods.keys())
                                    for modelName, model in self.__appSession[res["id"]][res["name"]].models.items()
                                }
                            }
                        )
                    elif res["job"] == "close":
                        self.__appSession.pop(res["id"])
                    elif res["job"] in ("compute", "method"):
                        targetView = self.__appSession[res["id"]][res["view"]]
                        targetModel = targetView.models[res["model"]]

                        for viewInfo in self.__appSession.values():
                            for view in viewInfo.values():
                                for model in view.models.values():
                                    await self.__send_ws(
                                        {
                                            "job": "update",
                                            "state": "success",
                                            "direction": "model",
                                            "id": res["id"],
                                            "view": res["view"],
                                            "model": res["model"],
                                            "variable": list(model.variables.keys())
                                        }
                                    )

                                    if view == targetView and model == targetModel:
                                        getRes = await self.__get_ws()
                                        for variable, value in getRes["variable"].items():
                                            exec("model.{} = value".format(variable))

                                        if res["job"] == "compute":
                                            model.computes[res["compute"]](self.__dataSession[res["id"]])
                                        elif res["job"] == "method":
                                            model.methods[res["method"]](self.__dataSession[res["id"]])

                                    await self.__send_ws(
                                        {
                                            "job": "update",
                                            "state": "success",
                                            "direction": "view",
                                            "id": res["id"],
                                            "view": res["view"],
                                            "model": model.name,
                                            "vars": {
                                                vName: var.value
                                                for vName, var in model.variables.items()
                                            }
                                        }
                                    )
                else:
                    print(res)

        self.__init_appDir(appDir)

    def __init_appDir(self, appDirPath:str):
        import os, sys
        from glob import glob
        from importlib import import_module
        from quart import Blueprint
        from .models import View

        appDirPath = os.path.abspath(appDirPath)
        if os.path.exists(appDirPath):
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

                        if key == "model":
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
                                    if line.strip().startswith("def ") or line.strip().startswith("@"):
                                        break

                                    if not line == "":
                                        lineSplit = [item for item in line.split("=")]
                                        modelLines[mlIdx] = "{0} = Variable({1})".format(lineSplit[0], lineSplit[1].strip())

                                insertSpace = modelLines[1].replace(modelLines[1].strip(), "")
                                modelLines.insert(1, insertSpace + "compute = binder.compute")
                                modelLines.insert(1, insertSpace + "method = binder.method")
                                modelLines.insert(1, insertSpace + "binder = Binder()")

                                pvInfo[key][modelLines[0][6:-8]] = "\n".join(modelLines)
                        else:
                            pvInfo[key] = "\n".join(blockStripLines)

            pvInfo["name"] = os.path.splitext(os.path.basename(pvFile))[0]

            prefixLine = pvt.split("\n")[0]
            if prefixLine.startswith("!prefix"):
                pvInfo["prefix"] = prefixLine[8:]
            else:
                pvInfo["prefix"] = "view"

            return pvInfo

    def __get_view_type(self, name:str) -> str:
        if name in self.__views.keys():
            return "view"
        elif name in self.__components.keys():
            return "component"

    async def __send_ws(self, sendInfo:dict):
        import json

        await self.__websocket.send(json.dumps(sendInfo))

    async def __get_ws(self) -> dict:
        import json

        try:
            res:dict = json.loads(await self.__websocket.receive())
            if not "state" in res.keys():
                res["state"] = "success"
        except json.decoder.JSONDecodeError:
            res = {
                "job": "error",
                "state": "failed"
            }

        return res

    def __create_viewFunc(self, fName, view):
        return """
def {0}():
    return '''
{1}
'''
""".format(fName, view.render())

    def start(self, host:str = "0.0.0.0", port:int = 8000):
        import os
        from quart import request

        @self.__app.route("/views/<viewName>")
        def showView(viewName):
            if viewName in self.__views.keys():
                return self.__views[viewName].render(request.remote_addr)
            else:
                return ""

        @self.__app.route("/components/<viewName>")
        def showComponent(viewName):
            if viewName in self.__components.keys():
                return self.__components[viewName].render(request.remote_addr)
            else:
                return ""

        self.__app.run(host = "0.0.0.0", port = port)
