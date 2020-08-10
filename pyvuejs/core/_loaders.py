# -*- coding: utf-8 -*-
import os, sys, json
import importlib
from typing import Dict, List, Tuple

from ._vue import VueInstance, VueComponent
from ..handlers import LoadingException


def load_app(project_dir:str, app_name:str, app_config:dict) -> VueInstance:
    if not "entry" in app_config.keys() or not "vue" in app_config.keys() or not "url" in app_config.keys():
        raise AttributeError("Please check config for \"model\", \"vue\", \"url\"!")

    if not "title" in app_config.keys():
        app_config["title"] = app_name

    vue_file = app_config.pop("vue") if "vue" in app_config.keys() else os.path.join("src", app_name, "index.vue")
    entry_name = os.path.splitext(os.path.basename(app_config.pop("entry")))[0]

    vue = VueInstance(
        os.path.join(project_dir, vue_file),
        getattr(importlib.import_module(f".{entry_name}", app_name), "__export__"),
        app_config
    )

    return vue

def load_component(component_lib) -> VueComponent:
    if hasattr(component_lib, "__export__"):
        return getattr(component_lib, "__export__")

    return None

def load_project(project_dir:str) -> Tuple[Dict[str, VueInstance], List[VueComponent], dict]:
    project_dir = os.path.abspath(project_dir)
    sys.path.append(project_dir)

    if not os.path.exists(os.path.join(project_dir, "config.py")):
        raise FileNotFoundError("Please check \"config.py\" exists!")

    configs = importlib.import_module("config")
    sys.path.remove(project_dir)

    src_dir = os.path.join(project_dir, "src")
    sys.path.append(src_dir)

    apps = {}
    for app_name, app_info in getattr(configs, "pages").items():
        apps[app_name] = load_app(project_dir, app_name, app_info)

    if len(apps) == 0:
        raise LoadingException("No valid apps!")

    component_dir = os.path.join(project_dir, "src", "components")

    components = []
    may_component_list = os.listdir(component_dir)
    for component_name in [os.path.splitext(name)[0] for name in may_component_list if not name == "__init__.py"]:
        component = load_component(importlib.import_module(f".{component_name}", "components"))
        if not component == None:
            components.append(component)

    sys.path.remove(src_dir)

    return apps, components, getattr(configs, "server")
