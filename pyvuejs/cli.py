"""Console script for pyvue."""
import os, sys
import zipfile
from .static import templateZip


def showHelp():
    print("""
//=========== pyvuejs help ===========//
· init
create project with templates

· start
start project

· build
build project to single executable
//====================================//
""")

def initProject():
    print("//=========== pyvuejs project init ===========//")
    appName:str = input("AppName: ")
    appDir = os.path.join(os.getcwd(), appName)
    if os.path.exists(appDir):
        raise RuntimeError("Directory {} already exists!".format(appName))
    else:
        os.mkdir(appDir)

    print("extracting template files....")
    zp = zipfile.ZipFile(templateZip)
    zp.extractall(appDir)
    zp.close()
    print("finished")

def startProject(args):
    print("//=========== start pyvuejs app ===========//")
    dirList = os.listdir(os.getcwd())
    if "manage.py" in dirList and "views" in dirList:
        if not "static" in dirList:
            print("static files are missing!")

        startArgs = args[1:]
        if len(startArgs) == 0:
            host = "0.0.0.0"
            port = 8000
        elif len(startArgs) == 1:
            if "." in startArgs[0] and len(startArgs[0].split(".")) == 4:
                host = startArgs[0]
                port = 8000
            else:
                host = "0.0.0.0"
                port = int(startArgs[0])
        else:
            host = startArgs[0]
            port = int(startArgs[1])

        os.system("{0} .\manage.py {1} {2}".format(
            sys.executable,
            "0.0.0.0" if host in ("127.0.0.1", "localhost") else host, port
        ))
    else:
        raise RuntimeError("Required files are missing! Please check \"manage.py\" file and \"views\" directory!")

def buildProject():
    raise RuntimeError("Build is not ready!")

def main(args):
    """Console script for pyvue."""
    args.pop(0)
    
    if len(args) > 0:
        if args[0] == "init":
            initProject()
        elif args[0] == "start":
            startProject(args)
        elif args[0] == "build":
            buildProject()
        else:
            showHelp()
    else:
        showHelp()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))  # pragma: no cover
