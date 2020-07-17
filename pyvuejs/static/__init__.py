# -*- coding: utf-8 -*-
import os
from . import __path__

baseView = open(os.path.join(__path__[0], "view.html"), "r", encoding = "utf-8").read()
templateZip = os.path.join(__path__[0], "template.zip")

del __path__
del os
