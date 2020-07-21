import sys, argparse
from .cli import main

args = argparse.ArgumentParser(description = "manage script of pyvuejs")
args.add_argument("job", help = "job to run app")
# appName(init)
args.add_argument("--app", default = "", help = "[init] name of app")
# host, port(run)
args.add_argument("--host", default = "0.0.0.0", help = "[run] host of backend server")
args.add_argument("--port", default = 8000, help = "[run] port of backend server")
args.add_argument("--logging", default = "enable", help = "[run] choose if logging to console")
args.add_argument("--mode", default = "server", help = "[run] mode of application")
args.add_argument("--window-size", default = "900,600", help = "[run] size of standalone window")
# type, name(create)
args.add_argument("--type", default = "plugin", help = "[create, remove] type of target(plugin, folder, file)")
args.add_argument("--name", default = "plugin1", help = "[create, remove] name of target")
# dist(build)
args.add_argument("--dist", default = "dist", help = "[build] build dist file location")

if __name__ == "__main__":
    try:
        sys.exit(main(vars(args.parse_args())))
    except KeyboardInterrupt:
        pass
