import os

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, OptionProperty, DictProperty, partial
from kivy.uix.behaviors import ButtonBehavior

from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.screen import MDScreen
from kivymd_extensions.akivymd.uix.dialogs import AKAlertDialog

from LightShare.libs.backend.urls import BASE_URL
from LightShare.libs.uix.baseclass.pages.demo import group as group_file
from LightShare.libs.uix.baseclass.pages import demo
from LightShare.libs.uix.baseclass.pages.demo.demo import profiles


class MessageScreen(Screen):
    """A screen that display the story fleets and all message histories."""


class CallScreen(Screen):
    """A screen that display the call histories."""


class StoryWithImage(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
    """A horizontal layout with an image(profile picture)
        and a text(username) - The Story."""

    text = StringProperty()
    source = StringProperty()


class GroupListItem(MDCard):
    """A clickable chat item for the group chat timeline."""

    isRead = OptionProperty(None, options=['delivered', 'read', 'new', 'waiting'])
    group_name = StringProperty()
    group_avatar = StringProperty()
    friend_mssg = StringProperty()
    timestamp = StringProperty()


class ChatBubble(MDBoxLayout):
    """A chat bubble for the chat screen messages."""

    profile = DictProperty()
    msg = StringProperty()
    time = StringProperty()
    sender = StringProperty()
    isRead = OptionProperty('waiting', options=['read', 'delivered', 'waiting'])


class ChatListItem(MDCard):
    '''A clickable chat item for the chat timeline.'''

    isRead = OptionProperty(None, options=['delivered', 'read', 'new', 'waiting'])
    friend_name = StringProperty()
    mssg = StringProperty()
    timestamp = StringProperty()
    friend_avatar = StringProperty()
    profile = DictProperty()
    chat_id = StringProperty()


class Message(MDLabel):
    """A adaptive text for the chat bubble."""


def chat_error(request, error):
    """Handle the error in the chat request."""
    print(f"[ERROR] Chat builder: {error}")


def story_error(request, error):
    """Handle the error in the story request."""
    print(f"[ERROR] Story builder: {error}")


class GroupsScreen(MDScreen):
    def __init__(self, **kwargs):
        super(GroupsScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/groups.kv')

    def load_groups(self):
        """Load the groups from the database."""
        if self.app.user_id != "":
            url = f'{BASE_URL}/{self.app.user_id}/people'
            print(f"[GET] {url}")
            # self.story_builder()
            UrlRequest(url, on_success=self.story_builder, on_error=story_error)
            url = f'{BASE_URL}/{self.app.user_id}/chats'
            UrlRequest(url, on_success=self.chatlist_builder, on_error=chat_error)

        # self.chatlist_builder()
        # self.grouplist_builder()

    def show_theme_picker(self):
        '''Display a dialog window to change app's color and theme.'''
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def story_builder(self, req, result):
        '''Create a Story for each user and
        adds it to the story layout'''
        print("[Story Builder] Result: ", result)
        self.ids['story_layout'].clear_widgets()

        for profile in result:
            self.story = StoryWithImage()
            self.story.text = result[profile]['name']
            self.story.bind(on_press=lambda x: self.story_click(profile))
            self.story.source = result[profile]['image_url']
            self.ids['story_layout'].add_widget(self.story)

    def story_click(self, other_id):
        """When a story is clicked, it opens the chat screen"""
        self.starting_conv_alert()
        self.other_id = other_id
        url = f'{BASE_URL}/{self.app.user_id}/people/{other_id}'
        UrlRequest(url, on_success=self.chat_screen, on_error=chat_error)
        # self.app.other_id = other_id
        # self.app.screen_manager.current = 'Chat'

    def chat_click(self, chat_id):
        self.other_id = chat_id
        url = f'{BASE_URL}/{self.app.user_id}/people/{chat_id}'
        UrlRequest(url, on_success=self.chat_screen, on_error=chat_error)

    def chat_screen(self, req, result):
        """Create a chat screen for the user"""
        self.app.chat_name = self.other_id
        self.app.chat_id = self.other_id
        chat_widget = self.manager.get_screen('chat')
        chat_widget.text = self.other_id
        chat_widget.image = 'https://storage.googleapis.com/lightshare-b528a.appspot.com/profile.png'
        chat_widget.active = True

        self.app.chat_id = result['conversation_id']
        print("[Chat Screen] Result: ", result)
        self.manager.current = 'chat'

    def chatlist_builder(self, req, result):
        """Create a Chat List Item for each user and
        adds it to the Conversations List"""
        print("[Chat List Builder] Result: ", result)
        self.ids['chatlist'].clear_widgets()
        for chat in result:
            # self.groupitem = GroupListItem()
            self.chatitem = ChatListItem()
            self.chatitem.profile = result[chat]
            self.chatitem.chat_id = chat
            self.chatitem.friend_name = result[chat]['name']
            self.chatitem.friend_avatar = result[chat]['image_url']
            self.chatitem.mssg = 'This is an example message'  # result[chat]['last_message']
            self.chatitem.timestamp = '14:37'  # result[chat]['last_message_time']
            self.chatitem.isRead = 'delivered'  # TODO: Live update
            self.chatitem.bind(on_release=lambda x: self.chat_click(result[chat]['other_id']))

            self.ids['chatlist'].add_widget(self.chatitem)

    def msg_builder(self, profile, screen):
        """Create a message bubble for creating chat."""
        for prof in profile['msg']:
            for messages in prof.split("~"):
                if messages != "":
                    message, time, isRead, sender = messages.split(";")
                    self.chatmsg = ChatBubble()
                    self.chatmsg.msg = message
                    self.chatmsg.time = time
                    self.chatmsg.isRead = isRead
                    self.chatmsg.sender = sender
                    screen.ids['msglist'].add_widget(self.chatmsg)
                else:
                    print("No message")

                print(self.chatmsg.isRead)

    def grouplist_builder(self):
        '''Create a Chat List Item for each group and
        adds it to the Group List'''

        # for messages in profiles:
        #     for message in messages['msg']:
        #         self.chatitem = ChatListItem()
        #         self.chatitem.profile = messages
        #         self.chatitem.friend_name = messages['name']
        #         self.chatitem.friend_avatar = messages['image']
        #
        #         lastmessage, time, isRead, sender = message.split(';')
        #         self.chatitem.mssg = lastmessage
        #         self.chatitem.timestamp = time
        #         self.chatitem.isRead = isRead
        #         self.chatitem.sender = sender
        #     self.ids['chatlist'].add_widget(self.chatitem)

    def starting_conv_alert(self):
        dialog = AKAlertDialog(
            header_icon="chat-plus",
            progress_interval=5,
            fixed_orientation="landscape",
            pos_hint={"center_x": 0.5, "top": 0.95},
            dialog_radius=0,
            size_landscape=["300dp", "70dp"],
            header_font_size="40dp",
            header_width_landscape="50dp",
            progress_color=[0.4, 0.1, 1, 1],
        )
        dialog.bind(on_progress_finish=dialog.dismiss)
        content = Factory.CreateNotification()
        content.ids.button.bind(on_release=dialog.dismiss)
        dialog.content_cls = content
        dialog.open()
