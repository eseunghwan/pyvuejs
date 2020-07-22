# -*- coding: utf-8 -*-
import os, sys
from glob import glob
from flask import Blueprint
from .logger import Logger
from .models import View

def interprete_pyvue(pvueFile) -> dict:
    with open(pvueFile, "r", encoding = "utf-8") as pvr:
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

                    if key == "model":
                        lineNums = []
                        for idx in range(len(blockStripLines)):
                            line = blockStripLines[idx]
                            if line.startswith("Model ") and line.endswith(":"):
                                lineNums.append(idx)
                                blockStripLines[idx] = "class {}(Model):".format(line[6:-1])
                            elif line.strip().startswith("def ") and line.endswith(":"):
                                mayDecoratorLine = blockStripLines[idx - 1].strip()
                                if mayDecoratorLine.startswith("@"):
                                    decoratorText = mayDecoratorLine.split("(")[0][1:]
                                    if decoratorText in ("method", "compute", "event"):
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
                            modelLines.insert(5, insertSpace + "WebView = WebView")
                            modelLines.insert(6, "")

                            pvInfo[key][modelLines[0][6:-8]] = "\n".join(modelLines)
                    else:
                        pvInfo[key] = "\n".join(blockStripLines)

        pvInfo["name"] = os.path.splitext(os.path.basename(pvueFile))[0]
        pvInfo["prefix"] = prefix

        return pvInfo

def interprete_appDir(appDir:str, serverApp, appSession:dict, webview, logging:bool):
    if logging:
        Logger.info("Interpreting app...")

    if os.path.exists(appDir):
        sys.path.append(appDir)

        if logging:
            Logger.info("Interpreting view files...")

        for pvPath in glob(os.path.join(appDir, "views", "*.pvue")):
            pvInfo = interprete_pyvue(pvPath)
            
            view:View = View(
                pvInfo["name"], pvInfo["prefix"],
                pvInfo["resource"], pvInfo["style"], pvInfo["script"],
                pvInfo["template"],
                pvInfo["model"],
                webview
            )

            if pvInfo["prefix"] == "view":
                appSession["views"][pvInfo["name"]] = view
            elif pvInfo["prefix"] == "component":
                appSession["components"][pvInfo["name"]] = view

            if logging:
                Logger.info("{}.pvue has been interpreted".format(pvInfo["name"]))

        if logging:
            Logger.info("Finished!\n")

        if logging:
            Logger.info("Linking static files to server...")

        staticDir = os.path.join(appDir, "static")
        if os.path.exists(staticDir):
            serverApp.register_blueprint(
                Blueprint(
                    os.path.basename(appDir), "pyvue",
                    static_url_path = "/app",
                    static_folder = staticDir
                )
            )
        if logging:
            Logger.info("Finished!\n")
    
    if logging:
        Logger.info("App has been ready!\n")
