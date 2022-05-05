import os

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class AllFilesScreen(MDScreen):
    id = 0
    user_name = StringProperty()
    def __init__(self, **kwargs):
        super(AllFilesScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/allfiles.kv')
