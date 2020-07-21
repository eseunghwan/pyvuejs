# -*- coding: utf-8 -*-
import logging

Logger = logging.Logger("pyvuejs")

__handler = logging.StreamHandler()
__handler.setFormatter(logging.Formatter("[%(name)s | %(asctime)s] %(levelname)s: %(message)s", datefmt = "%Y-%m-%dT%H:%M:%SZ"))
Logger.addHandler(__handler)

del logging
