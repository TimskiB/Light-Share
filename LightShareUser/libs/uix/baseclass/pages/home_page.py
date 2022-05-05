import os
from threading import Thread

from kivy import platform, garden
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core import clipboard
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.behaviors import RectangularRippleBehavior, MagicBehavior, HoverBehavior
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFloatingActionButton
from plyer import filechooser

from LightShare.libs.backend.upload import upload_content
from LightShare.libs.backend.urls import BASE_URL


def people_error(self):
    print("[People Builder] Error Building people builder")


class PeopleWithI(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
    """A horizontal layout with an image(profile picture)
        and a text(username) - The Story."""
    user_id = StringProperty()
    original_source = StringProperty()
    text = StringProperty()
    source = StringProperty()
    pressed = False

    def on_release(self):
        """When the user clicks on the image, change to an ticked image."""
        if not self.pressed:
            self.source = "./assets/images/checked.png"
            self.pressed = True
        else:
            self.source = self.original_source
            self.pressed = False


class ExampleWithIcon(MDBoxLayout):
    text = StringProperty()
    pressed = False


class AnimatedButton(Button, HoverBehavior):
    background = ListProperty((71 / 255, 104 / 255, 237 / 255, 1))
    sending = False

    def on_enter(self):
        if not self.sending:
            self.background = (0 / 255, 0.7 * 255 / 255, 0 / 255, 1)
            Animation(size_hint=(.35, .11), d=0.2).start(self)

    def on_leave(self):
        if not self.sending:
            self.background = (71 / 255, 104 / 255, 237 / 255, 1)
            Animation(size_hint=(.3, .10), d=0.2).start(self)

    def button_animation(self, float):
        self.text = "Sending..."
        self.sending = True
        self.background = (0 / 255, 0.7 * 255 / 255, 0 / 255, 1)
        Animation(size_hint=(1, 1), d=0.4).start(self)
        Animation(pos_hint={'center_x': .5, 'center_y': .5}, d=0.4).start(self)


class HomePage(MDScreen):
    user_name = StringProperty()
    send_data = {"files": [], "text": "", "media": []}
    cards = [False, False, False]
    custom_sheet = None

    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        # self.build()
        self.app = MDApp.get_running_app()
        self.user_id = self.app.user_id
        self.app.theme_cls.material_style = "M3"
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/home.kv')
        # self.ids.homme.add_widget(
        #     MDFloatingActionButton(
        #         icon='lan',
        #         type="standard",
        #         theme_icon_color="Custom",
        #         md_bg_color=get_color_from_hex("#e9dff7"),
        #         icon_color=get_color_from_hex("#211c29"),
        #     ))

    def get_user_data(self):
        url = f'{BASE_URL}/{self.app.user_id}/info'
        print(f"[GET] {url}")
        self.user_data = UrlRequest(url, on_success=self.on_user_data_success, on_error=self.on_user_data_error)

    def on_user_data_success(self, req, result):
        print(f"Result: {result}, Request: {req}")
        self.user_name = result['display_name']

    def on_user_data_error(self, req, result):
        print(result)

    # def on_enter(self):
    #     Thread(target=self.get_user_data).start()

    def go_profile(self):
        self.manager.current = 'profile'

    def get_clipboard(self):
        """Get the last item in the clipboard."""
        if self.cards[0]:
            # Disable the card
            self.cards[0] = False
            self.ids["clipboard_card"].md_bg_color = 1, 1, 1, 1
            self.send_data['text'] = ""
            return
        if data := Clipboard.paste():
            self.extracted_from_get_clipboard(data)
        else:
            print("No data in clipboard")

    # TODO Rename this here and in `get_clipboard`
    def extracted_from_get_clipboard(self, data):
        self.cards[0] = True
        self.send_data['text'] = data
        snack = Snackbar(
            text="Pasted From Clipboard",
            snackbar_x="10dp",
            snackbar_y="120dp",
            size_hint_x=.25,
            pos_hint={'center_x': .5},
            radius=[15, 15, 15, 15],

        )
        snack.ids.text_bar.font_name = 'DecaM'
        snack.ids.text_bar.halign = 'center'
        # snack.ids.text_bar.pos_hint = {'center_x': .5}
        snack.open()
        self.ids["clipboard_card"].md_bg_color = [0, 0.7, 0, 1]

    def upload_files(self):
        if self.cards[2]:
            # Disable the card
            self.cards[2] = False
            self.ids["files_card"].md_bg_color = 1, 1, 1, 1
            self.send_data['files'] = []
            return

        filechooser.open_file(multiple=True, on_selection=self.on_file_selection)

    def on_file_selection(self, paths):
        if paths:
            self.ids["files_card"].md_bg_color = [0, 0.7, 0, 1]
            self.cards[2] = True
            for path in paths:
                self.send_data['files'].append(path)
            print(f"Files: {self.send_data['files']}")

    def share(self):
        self.custom_sheet = MDCustomBottomSheet(
            radius=20,
            radius_from='top',
            animation=True,
            duration_opening=.3,
            screen=Factory.S()
        )
        self.sheet_ids = self.custom_sheet.children[0].children[0].children[0].ids
        self.sheet_ids["button"].bind(on_release=self.send_content)
        # self.custom_sheet.sheet_list.ids.box_sheet_list.padding = (dp(16), 0, dp(16), 0)
        self.custom_sheet._upper_padding = (0, 0, 0, 0)
        self.custom_sheet.open()
        url = f'{BASE_URL}/{self.app.user_id}/people'
        print(f"[GET] {url}")
        # self.story_builder()
        UrlRequest(url, on_success=self.people_builder, on_error=people_error)

    def send_content(self, instance):
        Clock.schedule_once(lambda dt: self.custom_sheet.dismiss(), 0.43)
        receiver_ids = [icon.user_id for icon in self.sheet_ids["people_share"].children if icon.pressed]
        print(f"Sending content to: {receiver_ids}")
        cloud_save = self.sheet_ids["switch"].active
        loading_id = self.manager.parent.parent.parent.ids.progress_percent
        loading_screen = self.manager.parent.parent.parent.ids.loading_window
        Thread(target=upload_content,
               # TODO: loading id
               args=(self.send_data, self.app.user_id, receiver_ids, self.app.device, loading_id, loading_screen, cloud_save)).start()
        self.send_data = {'text': "", 'files': []}

    def people_builder(self, req, result):
        """Create a Story for each user and
        adds it to the story layout"""
        print("[Person Builder] Result: ", result)
        sheet_ids = self.custom_sheet.children[0].children[0].children[0].ids
        sheet_ids['people_share'].clear_widgets()
        sheet_ids['people_share'].add_widget(ExampleWithIcon(text="New Chat"))
        for profile in result:
            self.story = PeopleWithI()
            self.story.text = result[profile]['name']
            self.story.user_id = profile
            self.story.source = result[profile]['image_url']
            self.story.original_source = result[profile]['image_url']
            sheet_ids['people_share'].add_widget(self.story)

    def go_lan(self):
        """Go to the LAN screen"""
        self.app.send_data = self.send_data
        self.manager.current = "lan"
