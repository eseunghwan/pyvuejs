# -*- coding: utf-8 -*-
from . import __path__

class Server():
    def __init__(self, appDir:str):
        import os, json
        from quart import Quart, websocket

        self.__views = {}
        self.__activatedViews = {}
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
                        self.__activatedViews[res["name"]] = self.__views[res["name"]]

                        await self.__send_ws(
                            {
                                "job": "init",
                                "state": "success",
                                "data": {
                                    modelName: {
                                        vName: var.value
                                        for vName, var in model.variables.items()
                                    }
                                    for modelName, model in self.__views[res["name"]].models.items()
                                }
                            }
                        )
                    elif res["job"] == "close":
                        self.__activatedViews.pop(res["name"])
                    elif res["job"] == "compute":
                        model = self.__views[res["view"]].models[res["model"]]
                        await self.__send_ws(
                            {
                                "job": "update",
                                "state": "success",
                                "direction": "model",
                                "view": res["view"],
                                "model": res["model"],
                                "variable": list(model.variables.keys())
                            }
                        )
                        getRes = await self.__get_ws()
                        for variable, value in getRes["variable"].items():
                            exec("model.{} = value".format(variable))

                        exec("model.{}()".format(res["method"]))

                        await self.__send_ws(
                            {
                                "job": "update",
                                "state": "success",
                                "direction": "view",
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
                
                self.__views[pvInfo["name"]] = View(
                    pvInfo["name"],
                    pvInfo["style"], pvInfo["script"],
                    pvInfo["template"],
                    pvInfo["model"]
                )

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
                "style": "",
                "template": "",
                "script": "",
                "model": []
            }
            for key in pvInfo.keys():
                try:
                    block = pvt.split("<{}>".format(key))[1].split("</{}>".format(key))[0]
                except IndexError:
                    block = ""

                if not block == "":
                    lines = block.split("\n")[1:-1]
                    stripLength = len(lines[0][:-1 * len(lines[0].strip())])

                    blockStripLines = [
                        line[stripLength:]
                        for line in lines
                    ]

                    if key == "model":
                        modelBlocks = {}

                        lineNums = []
                        for idx in range(len(blockStripLines)):
                            line = blockStripLines[idx]
                            if line.startswith("Model ") and line.endswith(":"):
                                lineNums.append(idx)
                                blockStripLines[idx] = "class {}(Model):".format(line[6:-1])

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
                                if line.strip().startswith("def "):
                                    break

                                if not line == "":
                                    lineSplit = [item for item in line.split("=")]
                                    modelLines[mlIdx] = "{0} = Variable({1})".format(lineSplit[0], lineSplit[1].strip())

                            modelBlocks[modelLines[0][6:-8]] = "\n".join(modelLines)

                        pvInfo[key] = modelBlocks
                    else:
                        pvInfo[key] = "\n".join(blockStripLines)

            pvInfo["name"] = os.path.splitext(os.path.basename(pvFile))[0]
            return pvInfo

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
        from quart import render_template_string

        # for modelName, model in Session.Models.items():
        #     pass

        for viewName, view in self.__views.items():
            fName = "show_{}".format(viewName)
            exec(self.__create_viewFunc(fName, view))

            self.__app.add_url_rule(
                "/views/{}".format(viewName),
                view_func = eval(fName)
            )
            # @self.__app.route("/views/{}".format(viewName))
            # def showView():
            #     return view.render()

        self.__app.run(host = "0.0.0.0", port = port)
