import os
import sys

from kivy.core.text import LabelBase

root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(root_dir, "libs", "applibs"))

import json  # NOQA: E402
import traceback  # NOQA: E402

from kivy.factory import Factory  # NOQA: E402
from lightshare import LightShare  # NOQA: E402

__version__ = "0.5"

"""
Registering factories from factory.json.
"""
r = Factory.register

#os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(root_dir, "libs", "backend", "ca_bundle.pem")
os.environ["SSL_CERT_FILE"] = os.path.join(root_dir, "libs", "backend", "certificate.pem")
with open("factory_registers.json") as fd:
    custom_widgets = json.load(fd)
    for module, _classes in custom_widgets.items():
        for _class in _classes:
            r(_class, module=module)


try:
    FONT_DIR = f"{os.path.dirname(__file__)}/assets/fonts/"
    LabelBase.register(name="DecaM", fn_regular=f"{FONT_DIR}LexendDeca-Medium.ttf")
    LabelBase.register(name="DecaL", fn_regular=f"{FONT_DIR}LexendDeca-Light.ttf")
    LabelBase.register(name="DecaB", fn_regular=f"{FONT_DIR}LexendDeca-Bold.ttf")
    LightShare().run()
except Exception:
    error = traceback.format_exc()

    """
    If the app encounters an error it automatically saves the
    error in a file called ERROR.log.
    You can use this for BugReport purposes.
    """
    with open("ERROR.log", "w") as error_file:
        error_file.write(error)

    print(error)
