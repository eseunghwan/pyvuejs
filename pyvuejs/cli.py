"""Console script for pyvue."""
import os, sys, zipfile, shutil, requests
import socket, errno
import sqlite3

from .static import project_template, app_template
from .logger import Logger
from .server import Server

def main(args):
    config_file = os.path.join(os.getcwd(), ".config")
    """Console script for pyvue."""
    if args["job"] == "create-project":
        Logger.info("Creating pyvuejs project...")
        
        app_root = os.path.join(os.getcwd(), args["name"])
        if os.path.exists(app_root):
            raise RuntimeError("Project {} already exists!".format(args["name"]))
        else:
            os.mkdir(app_root)

        Logger.info("Extracting template files...")
        zp = zipfile.ZipFile(project_template)
        zp.extractall(app_root)
        zp.close()

        Logger.info("Project \"{}\" is ready!\n".format(args["name"]))
    elif args["job"] == "create-app":
        Logger.info("Creating pyvuejs app...")

        app_dir = os.path.join(os.getcwd(), args["name"])
        if os.path.exists(app_dir):
            raise RuntimeError("App \"{}\" already exists!".format(args["name"]))
        else:
            os.mkdir(app_dir)

        Logger.info("Extracting template files...")
        zp = zipfile.ZipFile(app_template)
        zp.extractall(app_dir)
        zp.close()

        Logger.info("App \"{}\" is ready!\n".format(args["name"]))
    elif args["job"] == "remove-app":
        Logger.info("Removing app \"{}\"...".format(args["name"]))

        if args["name"] == "main":
            raise RuntimeError("App \"main\" cannot be removed!")

        app_dir = os.path.join(os.getcwd(), args["name"])
        if os.path.exists(app_dir):
            shutil.rmtree(os.path.join(os.getcwd(), args["name"]))
        else:
            raise RuntimeError("App \"{}\" not exists!".format(args["name"]))

        Logger.info("App \"{}\" removed!".format(args["name"]))

    elif args["job"] == "start":
        con = sqlite3.connect(config_file, check_same_thread = False)
        cursor = con.cursor()

        if cursor.execute("select count(*) from `state`;").fetchone()[0] > 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("127.0.0.1", int(args["port"])))
                cursor.execute("delete from `state`;")
                con.commit()
            except:
                raise RuntimeError("Server is already started!")

        cursor.execute("insert into `state` values ('{0}', {1});".format(
            args["host"], args["port"]
        ))
        con.commit()

        cursor.close()
        con.close()

        if args["mode"] == "server":
            Server(os.getcwd(), True).start(args["host"], int(args["port"]))
        elif args["mode"] == "standalone":
            Server(os.getcwd(), False).start_standalone(args["host"], int(args["port"]))
    elif args["job"] == "stop":
        con = sqlite3.connect(config_file, check_same_thread = False)
        cursor = con.cursor()

        if cursor.execute("select count(*) from `state`;").fetchone()[0] == 0:
            raise RuntimeError("Server not started!")
        
        Logger.info("Server is shutting down...")

        port = cursor.execute("select `port` from `state`;").fetchone()[0]
        requests.post("http://127.0.0.1:{}/stop".format(port))

        cursor.close()
        con.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))  # pragma: no cover
