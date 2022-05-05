import json
import os
import socket
import threading
from multiprocessing.pool import ThreadPool
from threading import Thread

import scapy.all as scapy
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.screen import MDScreen
import random

from LightShare.libs.backend.peer2peer.send import request_send
from LightShare.libs.uix.baseclass.main_screen import get_my_ip


class LocalPeople(ButtonBehavior, RectangularRippleBehavior, MDBoxLayout):
    """A horizontal layout with an image(profile picture)
        and a text(username) - The Story."""
    user_id = StringProperty()
    original_source = StringProperty()
    text = StringProperty()
    source = StringProperty()
    pressed = False
    data = {}

    def on_release(self):
        """When the user clicks on the image, change to an ticked image."""
        if not self.pressed:
            self.source = "./assets/images/checked.png"
            self.pressed = True
        else:
            self.source = self.original_source
            self.pressed = False


def scan(ip):
    arp_req_frame = scapy.ARP(pdst=ip)

    broadcast_ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout=1, verbose=False)[0]
    result = []
    for i in range(0, len(answered_list)):
        client_dict = {"ip": answered_list[i][1].psrc, "mac": answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result


def display_result(result):
    # print("-----------------------------------\nIP Address\tMAC Address\n-----------------------------------")
    local_addresses = [i["ip"] for i in result]
    # print(f"I have {len(local_addresses)} local addresses")
    return local_addresses


class LanScreen(MDScreen):
    addresses = {}
    showed_addresses = []
    local_users = {}
    id = 0
    y_pos = [0.4, 0.6, 0.8]
    x_pos = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]

    def __init__(self, **kwargs):
        super(LanScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/lan.kv')

    def lan_starter(self):
        self.addresses = {}
        self.showed_addresses = []
        self.local_users = {}
        for i in self.ids.lan_net.children:
            if type(i) == LocalPeople:
                self.ids.lan_net.remove_widget(i)

        self.my_ip = get_my_ip()
        self.ids.gif.anim_delay = 1 / 60
        self.ids.gif._coreimage.anim_reset(True)

        # Clock.schedule_once(self.add_device, 2)
        self.i = Clock.schedule_interval(self.look_for_devices_inte, 2.5)

    def lan_stopper(self):
        self.i.cancel()

    @mainthread
    def look_for_devices_inte(self, *args):
        pool = ThreadPool(processes=2)
        async_start = pool.apply_async(self.look_for_devices)
        # Thread(target=self.look_for_devices).start()

    def port_scanner(self, port, target):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            # print(f"Port {port} is open in {target}")
            if target not in self.addresses and target != self.my_ip:
                self.addresses[target] = port
        except:
            pass

    def look_for_devices(self, *args):
        """Look for devices on the network."""
        target = ".".join(get_my_ip().split(".")[:3]) + ".1/24"
        scanned_output = scan(target)
        addrs = display_result(scanned_output)

        for addr in addrs:
            target = addr  # scan local host
            for port in range(12340, 12360):
                thread = threading.Thread(target=self.port_scanner, args=[port, target, ])
                thread.start()
        for addr in self.addresses:
            if addr not in self.showed_addresses:
                t = threading.Thread(target=self.get_device_info, args=[addr, self.addresses[addr], ])
                t.start()

    def get_device_info(self, ip, port):
        print(f"[INFO] Getting info for device at {ip}:{port}")
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((ip, port))
            connection.send(json.dumps({
                "header": "info",
                "user_id": self.app.user_id
            }).encode("utf8"))
            if data := connection.recv(1024):
                data = json.loads(data.decode("utf8"))
                if data["header"] == "info":
                    self.showed_addresses.append(ip)
                    self.add_device(data, (ip, port))
            else:
                print(f"[ERROR]No data received from {ip}:{port}")
            connection.close()
        except Exception as e:
            print(f"\t[ERROR] Failed to find information about {ip}:{port} ({e})")

    def add_device(self, data, network_info):
        self.people = LocalPeople()
        self.people.text = data["display_name"]
        self.people.user_id = data["user_id"]
        data["network_info"] = network_info
        self.local_users[data["user_id"]] = data
        self.people.data = data
        self.people.original_source = "./assets/images/profile.png"
        self.people.source = "./assets/images/profile.png"
        self.people.pos_hint = {'center_x': random.choice(self.x_pos), 'center_y': random.choice(self.y_pos)}
        self.ids.lan_net.add_widget(self.people)

    def send_local(self):
        print(f"[INFO] Requesting to send to {len(self.local_users)} devices")
        selected = {
            d.data["user_id"]: d.data
            for d in self.ids.lan_net.children
            if type(d) == LocalPeople and d.pressed
        }

        if not selected:
            print("[ERROR] No devices to send to")
            return
        Thread(target=request_send, args=(selected, self.app.user_id, self.app.user_name, self.app.send_data,)) \
            .start()
        self.manager.current = "home"
        # TODO: Add a popup to show that the data is being sent

        # try:
        #     connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     connection.connect((ip, port))
        #     connection.send(json.dumps({
        #         "header": "info",
        #         "user_id": self.app.user_id
        #     }).encode("utf8"))
        #     if data := connection.recv(1024):
        #         data = json.loads(data.decode("utf8"))
        #         if data["header"] == "info":
        #             self.showed_addresses.append(ip)
        #             self.add_device(data)
        #     else:
        #         print(f"[ERROR]No data received from {ip}:{port}")
        #     connection.close()
        # except Exception as e:
        #     print(f"\t[ERROR] Failed to find information about {ip}:{port} ({e})")
