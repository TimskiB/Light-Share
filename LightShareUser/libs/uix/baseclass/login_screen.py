from kivy.animation import Animation
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.screen import MDScreen
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog

from LightShare.libs.backend.auth import Auth


class GoogleImage(Image):
    pass


class LoginScreen(MDScreen):
    """
    Example Screen.
    """
    RC_SIGN_IN = 999
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def home_page(self):
        self.manager.transition.direction = 'up'
        self.manager.current = 'home'

    def missing_login_info(self):
        dialog = AKAlertDialog(
            header_icon="text-short",
            header_bg=[0.9, 0, 0, 1],
            progress_interval=5,
            fixed_orientation="landscape",
            pos_hint={"right": 1, "y": 0.05},
            dialog_radius=0,
            opening_duration=5,
            size_landscape=["350dp", "70dp"],
            header_width_landscape="70dp",
        )
        dialog.bind(on_progress_finish=dialog.dismiss)
        content = Factory.Notification()
        content.ids.button.bind(on_release=dialog.dismiss)
        dialog.content_cls = content
        dialog.open()


    def show_error(self):
        """Show error message."""
        dialog = AKAlertDialog(
            header_icon="close-circle-outline", header_bg=[0.9, 0, 0, 1]
        )
        content = Factory.ErrorDialog()
        content.ids.button.bind(on_release=dialog.dismiss)
        dialog.content_cls = content
        dialog.open()


    @mainthread
    def email_login(self):
        """Add Authentication here."""
        self.auth = Auth()
        if self.ids.password.text and self.ids.email.text:
            if server_response := self.auth.email_sign_in(
                    self.ids.email.text, self.ids.password.text):
                if "error" in server_response:
                    self.show_error()
                    print(f"[ERROR] At sign in: {server_response}")
                else:
                    self.app.user_id = server_response['uid']
                    self.home_page()
            else:
                print("[ERROR] with server response at sign in.")

        else:
            self.missing_login_info()
            print("[ERROR] Password is empty.")
    # def login(self):
    #     """Add Authentication here."""
    #     self.manager.transition.direction = 'up'
    #     self.manager.current = 'home'
    #
    # def google_login(self):
    #     login_google(self.google, self.RC_SIGN_IN)
    #     self.current_provider = login_providers.google
    #
    # def after_login(self, name, email):
    #     self.manager.transition.direction = 'up'
    #     self.manager.current = 'home'
    #
    # def error_listener(self, error):
    #     print(error)
    #     self.manager.current = 'login'
