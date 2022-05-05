from kivy.factory import Factory
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog


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