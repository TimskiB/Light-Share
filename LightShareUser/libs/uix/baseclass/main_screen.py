import json
import os
import platform
import socket
import subprocess
from multiprocessing import Process
from threading import Thread

import requests
from kivy.animation import Animation
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.banner import MDBanner
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.button import MDFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd_extensions.akivymd.uix.bottomnavigation2 import Button_Item
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog

from LightShare.libs.backend.devices.device import create_error, on_device_error
from LightShare.libs.backend.listeners.event_listener import listen_for_events
from LightShare.libs.backend.peer2peer.send import receive_server
from LightShare.libs.backend.urls import BASE_URL
from LightShare.libs.uix.baseclass.pages.devices_page import DevicesScreen
from LightShare.libs.uix.baseclass.pages.files_page import FilesScreen
from LightShare.libs.uix.baseclass.pages.groups_page import GroupsScreen
from LightShare.libs.uix.baseclass.pages.home_page import HomePage
from LightShare.libs.uix.baseclass.pages.settings_page import SettingsScreen

from uuid import getnode as get_mac


class On_active_button(Button_Item):
    selected_item = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            for item in self.parent.children:
                if item.selected_item:
                    item.selected_item = False
            self.selected_item = True

        return super().on_touch_down(touch)


class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass


class MDFloatlayout():
    pass


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def on_event_error(req, result):
    print(f"\tEvent Error: {result}")


def copy_text(text):
    """Save text to clipboard"""
    from pyperclip import copy
    copy(text)
    print("Copied to clipboard")


def reset_event_sheet(ids):
    ids["clipboard_text"].text = 'No text was sent.'
    ids["copy_button"].disabled = True
    ids["file_text"].text = "No files were attached."
    ids["download_button"].disabled = True


def open_file(path):
    """Show path in native file explorer"""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Linux":
        subprocess.Popen(['xdg-open', path])
    elif platform.system() == "MacOS":
        subprocess.call(["open", path])
    else:
        print("Unknown OS, Cant open file")


class HomeScreen(MDScreen):
    """
    Example Screen.
    """
    id = 1
    controller = ObjectProperty()
    user_id = StringProperty()
    listener = False

    def __init__(self, **kw):
        super().__init__(**kw)
        # Often you need to get access to the application object from the view
        # class. You can do this using this attribute.
        self.app = MDApp.get_running_app()
        # Adding a view class as observer.
        # self.model.add_observer(self)

    def local_handler(self):
        self.app.socket.listen(5)
        while True:
            client, address = self.app.socket.accept()
            Thread(target=self.local_client_handler, args=(client, address)).start()

    def local_client_handler(self, client, address):
        while True:
            data = client.recv(1024)
            if not data:
                break
            data = json.loads(data.decode("utf8"))
            print(f"\tReceived data from {address}:\n{data}")
            if data["header"] == "info":
                client.send(
                    json.dumps(
                        {
                            "header": "info",
                            "display_name": self.app.user_name,
                            "user_id": self.app.user_id
                        }
                    ).encode("utf8")
                )
            elif data["header"] == "request_send":
                self.show_send_request(data, client)
        client.close()

    def show_send_request(self, info, other_socket):
        self.other_socket = other_socket
        Animation(blur=8, d=0.3).start(self)
        self.dialog = AKAlertDialog(
            header_icon="share-variant",
            size_landscape=["500dp", "300dp"],
            header_bg=[1, 87 / 100, 21 / 100, 1]
            # progress_interval=3,
        )

        self.dialog.bind(on_progress_finish=self.dialog.dismiss)
        content = Factory.SendRequest()
        content.ids.info.text = f"{info['user_name']} wants to send you a drop.\n{info['info']}"
        content.ids.accept.bind(on_release=self.receive_local)
        content.ids.reject.bind(on_release=self.reject_local)
        # content.bind(on_release=self.dialog.dismiss)

        self.dialog.content_cls = content
        self.dialog.open()

    def reject_local(self, instance):
        self.dialog.dismiss()
        Animation(blur=0, d=0.3).start(self)
        self.other_socket.send(
            json.dumps(
                {
                    "header": "request_reject",
                }
            ).encode("utf8")
        )

    def receive_local(self, instance):
        self.dialog.dismiss()
        Animation(blur=0, d=0.3).start(self)
        self.other_socket.send(
            json.dumps(
                {
                    "header": "request_accept",
                }
            ).encode("utf8")
        )
        Thread(target=self.local_receive).start()

    def local_receive(self):
        info = receive_server(self.app.path)
        print(f"\tReceived {info}")
        self.show_download_success("name", info["path"], "Light Drop received!")

    def download_files(self, files_info):
        for file_info in files_info:
            Thread(target=self.download_file, args=(files_info[file_info],)).start()

    def download_file(self, file_info):
        file_name = file_info['name']
        path = f"{self.app.path}\\uploads\\{file_name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        url = f"{BASE_URL}/{self.app.user_id}/download/{file_info['file_id']}"
        with open(path, 'wb') as f:
            f.write(requests.get(url).content)
        print(f"Saved {file_name} to {path}")
        self.show_download_success(file_name, path)

    def show_download_success(self, file_name, path, text="File downloaded successfully."):
        snack = Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="120dp",
            size_hint_x=.5,
            pos_hint={'center_x': .5},
            radius=[15, 15, 15, 15],

        )
        snack.buttons = [
            MDFlatButton(
                text="OPEN",
                theme_text_color="Custom",
                text_color=(0, 0.7, 0, 1),
                # md_bg_color=(0, 0.7, 0, 1),
                on_release=lambda dt: open_file(path),
            )]
        snack.ids.text_bar.font_name = 'DecaM'
        snack.ids.text_bar.halign = 'center'
        # snack.ids.tet
        snack.open()

    def show_device_dialog(self):
        Animation(blur=8, d=0.3).start(self)
        self.dialog = AKAlertDialog(
            header_icon="plus",
            size_landscape=["500dp", "300dp"],
            header_bg=[0, 0.7, 0, 1]
            # progress_interval=3,
        )
        self.dialog.bind(on_progress_finish=self.dialog.dismiss)
        content = Factory.DeviceDialog()
        content.ids.submit.bind(on_release=self.create_device)
        # content.bind(on_release=self.dialog.dismiss)

        self.dialog.content_cls = content
        self.dialog.open()

    def event_listener(self):
        """
        Listener for incoming messages.
        """
        self.listener = True
        event_getter = f'{BASE_URL}/{self.app.user_id}/event/'
        while True:
            event_key, event_data = listen_for_events(self.app)
            # if len(data) == 1 and 'example' in data and data['example'] == "example":
            #     print("\tThis was the example data.")
            # elif event_key := self.find_event_key(data):
            print(f"[GET] {event_getter}{event_key}")
            UrlRequest(f"{event_getter}{event_key}",
                       on_success=self.on_event_success,
                       on_error=on_event_error
                       )
            self.app.events[event_key] = event_data
            # else:
            #     print("\tEvents were already handled.")

    def on_event_success(self, req, result):
        print(f"\tHandling event: {result}")
        self.app.events[result['event_id']]["read"] = True
        self.notify_new_event(result)

    def notify_new_event(self, event):
        dialog = AKAlertDialog(
            header_icon="bell",
            progress_interval=5,
            fixed_orientation="landscape",
            pos_hint={"center_x": 0.5, "top": 0.95},
            dialog_radius=15,
            size_landscape=["300dp", "70dp"],
            header_font_size="40dp",
            header_width_landscape="50dp",
            progress_color=[0, 0.7, 0, 1],
            header_bg=[0, 0.7, 0, 1],
        )
        dialog.bind(on_progress_finish=dialog.dismiss)
        content = Factory.EventNotification()
        if event['sender-id'] == self.app.user_id:
            if event['sender-device'] == self.app.device:
                content.ids.event_text.text = "Your content was received."
            else:
                event['sender-name'] = "yourself."  # TODO: Get device name
                content.ids.event_text.text = f"You received content from another device ({event['sender-device']})."
        else:
            content.ids.event_text.text = f"{event['sender-name']} sent you content!"
        content.ids.button.bind(on_release=lambda dt: self.open_event(event))
        # content.ids.event_box.bind(on_release=lambda dt: self.open_event(event))
        # dialog.bind()
        dialog.content_cls = content
        dialog.open()

    def open_event(self, event_info):
        self.event_sheet = MDCustomBottomSheet(
            radius=20,
            radius_from='top',
            animation=True,
            duration_opening=.3,
            screen=Factory.Event()
        )

        self.sheet_ids = self.event_sheet.children[0].children[0].children[0].ids
        reset_event_sheet(self.sheet_ids)
        self.sheet_ids["event_title"].text = f"Received content from {event_info['sender-name']}:"
        if event_info["text"] != "":
            self.sheet_ids["clipboard_text"].text = event_info["text"]
            self.sheet_ids["copy_button"].disabled = False
            self.sheet_ids["copy_button"].bind(on_release=lambda dt: copy_text(event_info["text"]))
        if "files" in event_info:
            for file_info in event_info["files"]:
                info = f"{event_info['files'][file_info]['name']} (Size: {event_info['files'][file_info]['size']})"
                self.sheet_ids["file_text"].text = info
                self.sheet_ids["download_button"].disabled = False
                self.sheet_ids["download_button"].bind(on_release=lambda dt: self.download_files(event_info["files"]))
        # self.custom_sheet.sheet_list.ids.box_sheet_list.padding = (dp(16), 0, dp(16), 0)
        self.event_sheet._upper_padding = (0, 0, 0, 0)
        self.event_sheet.open()

    def find_event_key(self, data):
        """
        Check if any key in data does not exist in self.app.events.
        """
        for key in data:
            if key not in self.app.events and key != "example" and data[key]["read"] == False:
                return key
        return False

    def start_socket(self):
        port = 12345
        while True:
            try:
                self.app.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.app.socket.bind((get_my_ip(), 12345))
                break
            except OSError:
                port += 1

        Thread(target=self.local_handler).start()

    def check_device(self):
        # self.show_device_dialog()
        # self.my_mac = get_mac()
        # Start content listener
        Thread(target=self.start_socket).start()

        if not self.listener:
            self.listener = True
            self.listener_thread = Thread(target=self.event_listener)
            self.listener_thread.start()

        # self.open_event(None) # DEBUG
        uname = platform.uname()
        self.my_mac = uname.node
        self.app.device = self.my_mac

        url = f'{BASE_URL}/{self.app.user_id}/devices'
        print(f"[GET] {url}")
        self.user_data = UrlRequest(url, on_success=self.on_device_success, on_error=on_device_error)

    def on_device_success(self, req, result):
        devices = result["devices"]
        print(f"[INFO] Devices: {devices}")
        for device in devices:
            if devices[device]['mac'] == self.my_mac:
                print("[INFO] Device found in database.")
                return
        print("[INFO] Device not found in database.")
        self.show_device_dialog()

    def create_device(self, *args):
        name = self.dialog.content_cls.ids.device_name.text
        description = self.dialog.content_cls.ids.description.text

        url = f'{BASE_URL}/{self.app.user_id}/devices'
        print(f"[POST] {url}")

        # changed Content-type from application/x-www-form-urlencoded to application/json
        data = {'mac': self.my_mac,
                'name': name,
                'description': description}
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}
        params = json.dumps(data)
        self.user_data = UrlRequest(url, on_success=self.create_success, on_error=create_error,
                                    method='POST', req_body=params, req_headers=headers)

    def create_success(self, req, result):
        print("[INFO] Device created.")
        Animation(blur=0, d=0.6).start(self)
        self.dialog.dismiss()

    def start_title_change(self):
        for sub_screen in self.ids.scr.children:
            if sub_screen.name == "files":
                self.files_ids = sub_screen.ids
        if not self.parent.animation_started:
            self.parent.animation_started = True
            self.start()

        self.start()

    def start(self, *args):
        anim = Animation(opacity=1, duration=1)
        anim += Animation(opacity=1, duration=1.5)
        anim += Animation(opacity=0, duration=1)
        anim.bind(on_complete=self.start)
        # anim.start(self.files_ids[f"files_title{self.id}"])
        Animation.cancel_all(self.files_ids["files_title1"])
        anim.start(self.files_ids["files_title1"])
        self.id += 1
        if self.id == 3:
            self.id = 1

    def nav_back(self):
        self.ids.scr.current = "home"

    def get_user_data(self):
        if self.app.user_id != "":
            url = f'{BASE_URL}/{self.app.user_id}/info'
            print(f"[GET] {url}")
            self.user_data = UrlRequest(url, on_success=self.on_user_data_success, on_error=self.on_user_data_error)
        else:
            self.ids.scr.get_screen("home").user_name = "User"
            self.ids.scr.get_screen("profile").user_email = "Default"
            self.ids.scr.get_screen("allfiles").user_name = "User's Drive"

    def on_user_data_success(self, req, result):
        print(f"Result: {result}, Request: {req}")
        self.ids.scr.get_screen("home").user_name = result['data']['display_name']
        self.ids.scr.get_screen("profile").user_email = result['data']['email']
        # self.ids.scr.get_screen("home").ids.my_profile.source = result['data']['image_url']
        try:
            self.ids.scr.get_screen("profile").ids.user_image.source = result['data']['image_url']
        except:
            self.ids.scr.get_screen("profile").ids.user_image.source = "./assets/images/profile.png"
        self.ids.scr.get_screen("allfiles").user_name = f"{result['data']['display_name']}\'s Drive"
        self.app.user_name = result['data']['display_name']
        # self.user_name = result['data']['display_name']

    def on_user_data_error(self, req, result):
        print(f"[ERROR] {result}")

    def on_pre_enter(self):
        Thread(target=self.get_user_data).start()

    def change_color(self, instance):
        if instance in self.ids.values():
            current_id = list(self.ids.keys())[list(self.ids.values()).index(instance)]
            for i in range(4):
                if f"nav_icon{i + 1}" == current_id:
                    self.ids[f"nav_icon{i + 1}"].text_color = 1, 0, 0, 1
                else:
                    self.ids[f"nav_icon{i + 1}"].text_color = 0, 0, 0, 1

    def on_touch(self, instance):
        pass
        # for instance in self.root.ids.scr.children:
        # current_id = list(self.root.ids.values()).index(instance)
