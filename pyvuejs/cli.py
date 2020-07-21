"""Console script for pyvue."""
import os, sys, zipfile, shutil, requests
import socket, errno
import sqlite3
from .static import templateZip
from .logger import Logger

def main(args):
    stateFile = os.path.join(os.getcwd(), ".state")
    """Console script for pyvue."""
    if args["job"] == "init":
        Logger.info("Creating pyvuejs application...")
        if args["app"] == "":
            Logger.info("Please input AppName")
            args["app"] = input("AppName: ")

        appDir = os.path.join(os.getcwd(), args["app"])
        if os.path.exists(appDir):
            raise RuntimeError("App {} already exists!".format(args["app"]))
        else:
            os.mkdir(appDir)

        Logger.info("Extracting template files...")
        zp = zipfile.ZipFile(templateZip)
        zp.extractall(appDir)
        zp.close()

        Logger.info("App \"{}\" is ready!".format(args["app"]))

    elif args["job"] == "run":
        dirList = os.listdir(os.getcwd())
        if os.path.exists(stateFile):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("127.0.0.1", int(args["port"])))
                os.remove(stateFile)
            except:
                raise RuntimeError("Application is already started!")

        if "manage.py" in dirList and "views" in dirList:
            Logger.info("Starting pyvuejs application...")
            if not "static" in dirList:
                Logger.info("Static files are missing!")

            con = sqlite3.connect(stateFile, check_same_thread = False)
            cursor = con.cursor()
            cursor.execute("create table `state` (`PORT` INT);")
            cursor.execute("insert into `state` values ({});".format(args["port"]))
            con.commit()
            cursor.close()
            con.close()

            from .server import Server
            Server(os.getcwd()).start(args["host"], int(args["port"]))
        else:
            raise RuntimeError("Required files are missing! Please check \"manage.py\" file and \"views\" directory!")

    elif args["job"] == "stop":
        if os.path.exists(stateFile):
            con = sqlite3.connect(stateFile, check_same_thread = False)
            cursor = con.cursor()

            requests.post("http://127.0.0.1:{}/shutdown".format(
                cursor.execute("select `port` from `state`;").fetchone()[0]
            ))
            
            cursor.close()
            con.close()

            os.remove(stateFile)

    elif args["job"] == "create":
        Logger.info("Creating {0} {1}...".format(args["type"], args["name"]))
        if args["type"] == "plugin":
            targetDir = os.path.join(os.getcwd(), "plugins", args["name"])
            if not os.path.exists(targetDir):
                os.mkdir(targetDir)
                with open(os.path.join(targetDir, "__init__.py"), "w", encoding = "utf-8") as initW:
                    initW.write("# -*- coding: utf-8 -*-\n")

                Logger.info("Plugin {0} is ready!".format(args["name"]))
            else:
                Logger.warn("Plugin {0} already exists!".format(args["name"]))
        elif args["type"] == "folder":
            targetDir = os.path.join(os.getcwd(), args["name"])
            if not os.path.exists(targetDir):
                os.mkdir(targetDir)
                Logger.info("Folder {0} is created!".format(args["name"]))
            else:
                Logger.warn("Folder {0} already exists!".format(args["name"]))
        elif args["type"] == "file":
            targetFile = os.path.join(os.getcwd(), args["name"])
            if not os.path.exists(targetFile):
                with open(targetFile, "w", encoding = "utf-8") as fileW:
                    fileW.write("")

                Logger.info("File {0} is created!".format(args["name"]))
            else:
                Logger.warn("Fild {0} already exists!".format(args["name"]))

    elif args["job"] == "remove":
        Logger.info("Removing {0} {1}...".format(args["type"], args["name"]))
        if args["type"] in ("plugin", "folder"):
            targetDir = os.path.join(os.getcwd(), "plugins", args["name"]) if args["type"] == "plugin" else os.path.join(os.getcwd(), args["name"])
            if os.path.exists(targetDir):
                shutil.rmtree(targetDir)
                Logger.info("{0} {1} is removed!".format(args["type"].capitalize(), args["name"]))
        elif args["type"] == "file":
            targetFile = os.path.join(os.getcwd(), args["name"])
            if os.path.exists(targetFile):
                os.remove(targetFile)
                Logger.info("File {0} is removed!".format(args["name"]))

if __name__ == "__main__":
    sys.exit(main(sys.argv))  # pragma: no cover
