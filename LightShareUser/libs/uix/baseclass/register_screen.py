from kivy.animation import Animation
from kivy.core.image import Image
from kivy.factory import Factory
from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.behaviors import CircularRippleBehavior, RectangularRippleBehavior, BackgroundColorBehavior, \
    HoverBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog

from LightShare.libs.backend.auth import Auth


class RectangularRippleButton(MDBoxLayout,
                              RectangularRippleBehavior, ButtonBehavior, BackgroundColorBehavior
                              ):
    pass


class RectangularRippleImage(CircularRippleBehavior, ButtonBehavior, Image):
    pass


class RegisterScreen(MDScreen):
    """
    Example Screen.
    """

    def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        super(RegisterScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def home_page(self):
        self.manager.current = 'home'

    def sign_up(self):
        self.auth = Auth()
        if self.ids.password.text == self.ids.confirm_password.text:
            if server_response := self.auth.email_sign_up(
                    self.ids.email.text, self.ids.password.text, self.ids.username.text
            ):
                if "error" in server_response:
                    self.show_error()
                else:
                    print(f"""[UID] {server_response["uid"]}""")
                    self.app.user_id = server_response["uid"]
                    self.manager.transition.direction = 'up'
                    self.manager.current = 'home'
            else:
                print("Error with server response at sign up")

        else:
            self.mismatch()
            print("Passwords do not match")

    def mismatch(self):
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
        content = Factory.NNotification()
        content.ids.button.bind(on_release=dialog.dismiss)
        dialog.content_cls = content
        dialog.open()


    def show_error(self):
        """Show error message."""
        dialog = AKAlertDialog(
            header_icon="close-circle-outline", header_bg=[0.9, 0, 0, 1]
        )
        content = Factory.EErrorDialog()
        content.ids.button.bind(on_release=dialog.dismiss)
        dialog.content_cls = content
        dialog.open()