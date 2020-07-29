# -*- coding: utf-8 -*-
import os, sys, gc
from collections import OrderedDict
from copy import copy, deepcopy
from flask import Flask, redirect, request, jsonify, __path__ as __flask_path__
import logging, json, json_logging
from datetime import datetime, timedelta
from threading import Thread
import webview as pywebview

from . import __path__
from .logger import Logger
from .interpreter import Interpreter

class Server():
    def __init__(self, app_root:str, enable_logging:bool = True):
        gc.enable()
        self.__logging = enable_logging

        if self.__logging:
            Logger.info("Preparing server...\n")

        self.__app_root = os.path.abspath(app_root)
        self.__session = {
            "server": {
                "mpa": OrderedDict(),
                "upload_time": {}
            },
            "app": {
                "views": OrderedDict(),
                "components": OrderedDict()
            },
            "data": OrderedDict()
        }
        self.__config = {
            "expired_time": 1800
        }

        self.__server = Flask(
            "pyvuejs",
            static_folder = os.path.join(__path__[0], "static")
        )
        self.__server_thread = None
        self.__cef_view = None
        # self.__server.secret_key = os.urandom(16)

        self.__set_routes()
        self.__get_project_info()

    def __set_routes(self):
        if self.__logging:
            Logger.info("Setting routing points...")

        @self.__server.before_request
        def job_before_request():
            gc.collect()

        @self.__server.after_request
        def job_after_request(response):
            gc.collect()
            return response

        @self.__server.route("/")
        def show_index():
            return redirect("/views/main")

        @self.__server.route("/stop", methods = ["POST"])
        def stop_server():
            if self.__logging:
                Logger.info("Stopping server...")

            sys.exit()

        if self.__logging:
            Logger.info("Setting view/component points...")

        @self.__server.route("/views/<view_name>")
        def show_view(view_name:str):
            if view_name in self.__session["app"]["views"].keys():
                view_id = request.remote_addr
                if not view_id in self.__session["data"].keys():
                    self.__session["data"][view_id] = {}

                if not view_id in self.__session["server"]["mpa"].keys():
                    self.__session["server"]["mpa"][view_id] = {}

                if not view_name in self.__session["server"]["mpa"][view_id].keys():
                    self.__copy_model(view_id, "view", view_name)

                    for model in self.__session["server"]["mpa"][view_id][view_name]["models"].values():
                        if not self.__cef_view == None:
                            model.webview = self.__cef_view

                        for var_name, variable in model.sessions.items():
                            self.__session["data"][view_id][var_name] = variable

                        if "load" in model.events.keys():
                            model.call_event("load", self.__session["data"][view_id])

                for model in self.__session["server"]["mpa"][view_id][view_name]["models"].values():
                    if "show" in model.events.keys():
                        model.call_event("show", self.__session["data"][view_id])

                return self.__session["server"]["mpa"][view_id][view_name]["view"].render(
                    view_id,
                    list(self.__session["server"]["mpa"][view_id][view_name]["models"].keys())
                )
            else:
                return ""

        @self.__server.route("/components/<component_name>")
        def show_component(component_name:str):
            if component_name in self.__session["app"]["components"].keys():
                component_id = request.remote_addr
                if not component_id in self.__session["data"].keys():
                    self.__session["data"][component_id] = {}

                if not component_id in self.__session["server"]["mpa"].keys():
                    self.__session["server"]["mpa"][component_id] = OrderedDict()

                if not component_name in self.__session["server"]["mpa"][component_id].keys():
                    self.__copy_model(component_id, "component", component_name)

                    for model in self.__session["server"]["mpa"][component_id][component_name]["models"].values():
                        if not self.__cef_view == None:
                            model.webview = self.__cef_view

                        for var_name, variable in model.sessions.items():
                            self.__session["data"][component_id][var_name] = variable

                        if "load" in model.events.keys():
                            model.call_event("load", self.__session["data"][component_id])

                for model in self.__session["server"]["mpa"][component_id][component_name]["models"].values():
                    if "show" in model.events.keys():
                        model.call_event("show", self.__session["data"][component_id])

                return self.__session["server"]["mpa"][component_id][component_name]["view"].render(
                    component_id,
                    list(self.__session["server"]["mpa"][component_id][component_name]["models"].keys())
                )
            else:
                return ""

        if self.__logging:
            Logger.info("Setting function points...")

        @self.__server.route("/functions/init_view", methods = ["POST"])
        def job_init_view():
            res = json.loads(request.data)

            if res["id"] in self.__session["server"]["mpa"].keys():
                view_info = self.__session["server"]["mpa"][res["id"]][res["name"]]
                return jsonify({
                    "state": "success",
                    "session": self.__session["data"][res["id"]],
                    "data": {
                        model_name: model.variables
                        for model_name, model in view_info["models"].items()
                    },
                    "methods": {
                        model_name: list(model.methods.keys())
                        for model_name, model in view_info["models"].items()
                    }
                })

            return jsonify({ "state": "failed" })

        @self.__server.route("/functions/method", methods = ["POST"])
        def job_call_method():
            res = json.loads(request.data)

            if res["id"] in self.__session["server"]["mpa"].keys():
                view_info = self.__session["server"]["mpa"][res["id"]][res["name"]]
                model = view_info["models"][res["model"]]

                model.call_method(res["method"], self.__session["data"][res["id"]])

                return jsonify({ "state": "success" })

            return jsonify({ "state": "failed" })

        @self.__server.route("/functions/upload_variable", methods = ["POST"])
        def job_upload_variable():
            res = json.loads(request.data)

            if res["id"] in self.__session["server"]["mpa"].keys():
                view_info = self.__session["server"]["mpa"][res["id"]][res["name"]]
                for model_name, variables in res["variable"].items():
                    model = view_info["models"][model_name]
                    for var_name, value in variables.items():
                        model.variables[var_name] = value

                return jsonify({ "state": "success" })

            return jsonify({ "state": "failed" })

        @self.__server.route("/functions/download_variable", methods = ["POST"])
        def job_download_variable():
            res = json.loads(request.data)

            if res["id"] in self.__session["server"]["mpa"].keys():
                view_info = self.__session["server"]["mpa"][res["id"]][res["name"]]
                return jsonify({
                    "state": "success",
                    "variable": {
                        model_name: model.variables
                        for model_name, model in view_info["models"].items()
                    }
                })

            return jsonify({ "state": "failed" })

        @self.__server.route("/functions/upload_session", methods = ["POST"])
        def job_upload_session():
            res = json.loads(request.data)

            if res["id"] in self.__session["data"].keys():
                self.__session["data"][res["id"]] = res["session"]
                self.__session["server"]["upload_time"][res["id"]] = datetime.now()

                return jsonify({ "state": "success" })

            return jsonify({ "state": "failed" })

        @self.__server.route("/functions/download_session", methods = ["POST"])
        def job_download_session():
            res = json.loads(request.data)

            for view_id in self.__session["data"].keys():
                if view_id in self.__session["server"]["upload_time"]:
                    last_update_time = self.__session["server"]["upload_time"][view_id]
                    time_delta = timedelta(seconds = self.__config["expired_time"])

                    if last_update_time + time_delta < datetime.now():
                        self.__session["data"].pop(view_id)
                        self.__session["server"]["mpa"].pop(view_id)
                else:
                    self.__session["server"]["upload_time"][view_id] = datetime.now()

            if res["id"] in self.__session["data"].keys():
                return jsonify({
                    "state": "success",
                    "session": self.__session["data"][res["id"]]
                })

            return jsonify({ "state": "failed" })

        if self.__logging:
            Logger.info("finished\n")

    def __get_project_info(self):
        project_info = Interpreter(self.__app_root, self.__server, self.__logging).interprete()
        for view_name, view_info in project_info.items():
            self.__session["app"]["{}s".format(view_info["view"].prefix)][view_name] = view_info

    def __copy_model(self, view_id:str, view_prefix:str, view_name:str):
        try:
            self.__session["server"]["mpa"][view_id][view_name] = deepcopy(self.__session["app"]["{}s".format(view_prefix)][view_name])
        except TypeError as err:
            if err.args[0].startswith("can't pickle"):
                self.__session["server"]["mpa"][view_id][view_name] = copy(self.__session["app"]["{}s".format(view_prefix)][view_name])

    def __start_thread(self):
        self.__server.run(
            host = self.__config["host"],
            port = self.__config["port"],
            debug = False
        )

    def start(self, host:str, port:int, no_wait:bool = False):
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        self.__config["host"] = "0.0.0.0" if host in ("127.0.0.1", "localhost") else host
        self.__config["port"] = port
        if self.__logging:
            Logger.info("Server started on \"http://{}:{}/\"".format(
                "127.0.0.1" if host == "0.0.0.0" else host, port
            ))
            Logger.info("Please check Devtool to show data transfers")

        self.__server_thread = Thread(target = self.__start_thread)
        self.__server_thread.start()

        if not no_wait:
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass

            self.stop()

    def start_standalone(self, host:str, port:int):
        Logger.info("Start server on background...")
        self.start(host, port, True)

        Logger.info("Setting up webview...")
        webview_icon = os.path.join(self.__app_root, "static", "favicon.ico")
        if not os.path.exists(webview_icon):
            webview_icon = os.path.join(__path__[0], "static", "favicon.ico")

        pywebview.create_window(
            os.path.basename(self.__app_root),
            "http://127.0.0.1:{}/".format(port),,
            width = 950, height = 650
        )

        Logger.info("Webview is loaded")
        pywebview.start()

        Logger.info("Shutting down background server...")
        self.stop()

    def stop(self):
        import sqlite3
        con = sqlite3.connect(os.path.join(self.__app_root, ".config"))
        cursor = con.cursor()
        cursor.execute("delete from `state`;")
        cursor.close()
        con.close()

        sys.exit()
