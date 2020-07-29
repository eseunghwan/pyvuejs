# -*- coding: utf-8 -*-
import os, sys, types
from glob import glob
from flask import Blueprint
from .logger import Logger
from .models import View, Model
import importlib


class Interpreter():
    def __init__(self, app_root:str, server, logging:bool = True):
        self.__app_root = app_root
        self.__server = server
        self.__logging = logging

    def interprete_view(self, view_file:str) -> dict:
        view_parsed = {}
        if self.__logging:
            Logger.info("Interpreting pvue file...")

        with open(view_file, "r", encoding = "utf-8") as vfr:
            vft = vfr.read()

        if vft.startswith("!prefix"):
            view_parsed["prefix"] = vft.splitlines()[0][7:].strip()
        else:
            view_parsed["prefix"] = "view"
        
        for block_name in ["resources", "style", "template"]:
            start_tag, end_tag = "<{}>".format(block_name), "</{}>".format(block_name)
            if start_tag in vft and end_tag in vft:
                view_parsed[block_name] = vft.split(start_tag)[1].split(end_tag)[0]
            else:
                view_parsed[block_name] = ""

        if self.__logging:
            Logger.info("finished")

        return view_parsed

    def load_models(self, app_name:str) -> dict:
        models_loaded = {}
        if self.__logging:
            Logger.info("Interpreting models...")

        models = importlib.import_module(".models", app_name)
        for may_model_name in [mname for mname in dir(models) if not mname == "Model" and not mname.startswith("_")]:
            # try:
            # may_model = eval("models.{}".format(may_model_name))
            may_model = getattr(models, may_model_name)
            if "__class_type__" in dir(may_model):
                models_loaded[may_model_name] = may_model()
                if self.__logging:
                    Logger.info("Model {} loaded".format(may_model_name))
            # except:
            #     pass

        if self.__logging:
            Logger.info("finished\n")

        return models_loaded

    def link_static(self):
        if os.path.exists(os.path.join(self.__app_root, "static")):
            if self.__logging:
                Logger.info("Linking static to server...")

            self.__server.register_blueprint(
                Blueprint(
                    os.path.basename(self.__app_root), "pyvue",
                    static_url_path = "/app",
                    static_folder = os.path.join(self.__app_root, "static")
                )
            )

            if self.__logging:
                Logger.info("finished\n")
        else:
            if self.__logging:
                Logger.warn("Static files are missing!\n")

    def load_app(self, app_name:str) -> dict:
        if self.__logging:
            Logger.info("Interpreting app \"{}\"...".format(app_name))

        view_parsed = self.interprete_view(os.path.join(self.__app_root, app_name, "view.html"))
        models_loaded = self.load_models(app_name)

        return {
            "view": View(
                view_parsed["prefix"], app_name,
                view_parsed["template"],
                view_parsed["resources"], view_parsed["style"]
            ),
            "models": models_loaded
        }

    def interprete(self) -> dict:
        interpreted = {}

        if self.__logging:
            Logger.info("Interpreting project \"{}\"...\n".format(os.path.basename(self.__app_root)))

        sys.path.append(self.__app_root)
        may_apps = list(os.walk(self.__app_root))[0][1]
        if not "main" in may_apps:
            raise RuntimeError("App \"main\" not exists!")

        for app_name in may_apps:
            try:
                exec("from {} import __package_type__".format(app_name))
                interpreted[app_name] = None
            except:
                pass

        for app_name in interpreted.keys():
            interpreted[app_name] = self.load_app(app_name)

        self.link_static()

        if self.__logging:
            Logger.info("Project is ready!\n")

        return interpreted
