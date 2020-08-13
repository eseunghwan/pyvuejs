# -*- coding: utf-8 -*-
import os, signal
from threading import Thread
from bottle import route, response, redirect, run
from webbrowser import open_new

from ..static import static_dir
from ..webview import WebViewUtils, start as webview_start

class Server():
    def __init__(self, project_dir:str):
        self.__project_dir = project_dir
        self.__project_name = os.path.basename(project_dir)

        @route("/static/<static_file>")
        def serve_static_file(static_file:str):
            file_ext = os.path.splitext(static_file)[1][1:]
            static_file = os.path.join(static_dir, static_file)

            if os.path.exists(static_file):
                if file_ext == "ico":
                    response.set_header("Content-type", "image/x-icon")
                    return open(static_file, "rb").read()
                elif file_ext == "js":
                    response.set_header("Content-type", "text/javascript")
                else:
                    response.set_header("Content-type", "text/{}".format(file_ext))

                return open(static_file, "r", encoding = "utf-8").read()
            else:
                return "static files: " + ", ".join(os.listdir(static_dir))

    def __start(self, host:str, port:int):
        run(
            host = host, port = port,
            quiet = True
        )

    def start(self, host:str = None, port = None, wait_server:bool = True, open_browser:bool = False):
        if host == None:
            host = "0.0.0.0"

        if port == None:
            # pyvuejs -> pvuejs -> 047372 -> 47372
            port = 47372

        Thread(target = self.__start, args = (host, port), daemon = True).start()

        if open_browser:
            open_new(f"http://127.0.0.1:{port}/default_app")

        if wait_server:
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                self.__class__.stop()

        return host, port

    def start_standalone(self, default_app:str = None, host:str = None, port = None, width:int = 950, height:int = 650):
        if default_app == None:
            default_app = "default_app"

        host, port = self.start(host, port, False)

        WebViewUtils.create_window(
            self.__project_name, f"http://127.0.0.1:{port}/{default_app}",
            width = width, height = height
        )

        webview_icon = os.path.join(self.__project_dir, "public", "favicon.png")
        if not os.path.exists(webview_icon):
            webview_icon = os.path.join(static_dir, "favicon.png")

        webview_start(webview_icon)
        self.__class__.stop()

    @staticmethod
    @route("/stop")
    def stop():
        os.kill(os.getpid(), signal.SIGTERM)
