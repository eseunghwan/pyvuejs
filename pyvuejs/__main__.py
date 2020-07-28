import sys, argparse
from .cli import main

args = argparse.ArgumentParser(description = "manage script of pyvuejs")
args.add_argument("job", help = "job[\"create-project\", \"create-app\", \"start\", \"stop\"]")
args.add_argument("--name", help = "name for create")
args.add_argument("--host", default = "0.0.0.0", help = "host for server")
args.add_argument("--port", default = 8080, help = "port for server")
args.add_argument("--mode", default = "server", help = "mode for server[\"server\", \"standalone\"]")

if __name__ == "__main__":
    try:
        sys.exit(main(vars(args.parse_args())))
    except KeyboardInterrupt:
        pass
