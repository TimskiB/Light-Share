import os
from threading import Thread

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from LightShare.libs.backend.urls import BASE_URL

def info_error(self, error):
    print("[ERROR] Failed getting files info.")
def get_size(bytes_number):
    """Convert bytes to gigabytes with 2 decimal places."""
    if bytes_number <= 0:
        return "0.00"
    size = bytes_number / (1024 * 1024 * 1024)
    return "{:.2f}".format(size)


class FilesScreen(MDScreen):
    id = 0

    def __init__(self, **kwargs):
        super(FilesScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/files.kv')

    # def build(self):
    #     return Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/files.kv')
    def on_pre_enter(self):
        # self.username = UrlRequest(
        pass

    def start_title_change(self):
        # for sub_screen in self.ids.scr.children:
        #     if sub_screen.name == "files":
        #         self.files_ids = sub_screen.ids
        Thread(target=self.start).start()
        url = f"{BASE_URL}/{self.app.user_id}/files-info"
        UrlRequest(url, on_success=self.files_info_callback, on_error=info_error)

    def files_info_callback(self, request, result):
        if "size" in result:
            self.ids.storage_title.text = f"{get_size(result['size'])} GB of 15 GB Used"
            self.ids.storage_bar.value = float(get_size(result['size']))/15*100
    def start(self, *args):
        anim = Animation(opacity=1, duration=1)
        anim += Animation(opacity=1, duration=1.5)
        anim += Animation(opacity=0, duration=1)
        anim.bind(on_complete=self.start)
        # anim.start(self.files_ids[f"files_title{self.id}"])
        Animation.cancel_all(self.ids["files_title1"])
        anim.start(self.ids["files_title1"])
        self.id += 1
        if self.id == 3:
            self.id = 1

    def all_files(self):
        self.manager.current = "allfiles"
