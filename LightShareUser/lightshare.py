import os
import platform

from kivy.core.window import Window
from kivy.properties import StringProperty
from kivymd.app import MDApp

from libs.uix.baseclass.root import Root

# This is needed for supporting Windows 10 with OpenGL < v2.0
if platform.system() == "Windows":
    os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"


class LightShare(MDApp):  # NOQA: N801
    animation_started = False
    path = os.getcwd()

    user_id = StringProperty()
    user_name = StringProperty()

    chat_id = StringProperty()
    chat_name = StringProperty()

    client_socket = None
    events = {}
    send_data = {}
    device = None

    def __init__(self, **kwargs):
        super(LightShare, self).__init__(**kwargs)
        Window.soft_input_mode = "below_target"
        self.title = "Light Share"

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "A700"

        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.accent_hue = "400"

        # self.theme_cls.theme_style = "Dark"

    def build(self):
        self.icon = 'icon.ico'
        return Root()
