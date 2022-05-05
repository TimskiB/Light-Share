import os

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd_extensions.akivymd.uix.silverappbar import AKSilverAppbar


Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/profile.kv')


class SettingsScreen(MDScreen):
    user_email = StringProperty()
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        pass

