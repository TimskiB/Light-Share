import os

from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen

from LightShare.libs.backend.urls import BASE_URL


class ElementCard(MDCard):
    device_id = StringProperty()
    image = StringProperty()
    text = StringProperty()
    subtext = StringProperty()
    items_count = StringProperty()


class DeviceCard(MDCard):
    name = StringProperty()
    description = StringProperty()
    device_id = StringProperty()


def collect_devices_error(req, result):
    print(f"Error collecting devices: {result}")


class DevicesScreen(MDScreen):
    def __init__(self, **kwargs):
        super(DevicesScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/devices.kv')

    def get_devices(self):
        url = f'{BASE_URL}/{self.app.user_id}/devices'
        UrlRequest(url, on_success=self.devices_collected, on_error=collect_devices_error)

    def devices_collected(self, req, result):
        self.ids.devices_grid.clear_widgets()
        devices = result["devices"]
        for device in devices:
            c = str(devices[device]["events"])
            card = ElementCard(
                image="./assets/images/devices/device1.png",  # TODO: change to device image
                text=devices[device]["name"],
                subtext=devices[device]["description"],
                items_count=f"{c} Events",
                device_id=devices[device]["device_id"]
            )
            #  card.bind(on_release=self.open_device_page)  #TODO: add on_release event
            self.ids.devices_grid.add_widget(card)
