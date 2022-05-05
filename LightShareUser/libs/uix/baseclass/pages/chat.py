import os

from kivy.lang import Builder
from kivy.properties import StringProperty, DictProperty, OptionProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from LightShare.libs.uix.baseclass.pages.demo.demo import profiles


class ChatBubble(MDBoxLayout):
    msg = StringProperty()
    time = StringProperty()
    sender = StringProperty()
    isRead = OptionProperty('waiting', options=['read', 'delivered', 'waiting'])


class Message(MDLabel):
    pass


# class ChatListItem(MDCard):
#     '''A clickable chat item for the chat timeline.'''
#
#     isRead = OptionProperty(None, options=['delivered', 'read', 'new', 'waiting'])
#     friend_name = StringProperty()
#     msg = StringProperty()
#     timestamp = StringProperty()
#     friend_avatar = StringProperty()
#     profile = DictProperty()

Builder.load_file(f'{os.getcwd()}/libs/uix/kv/mainpages/chat.kv')


class ChatScreen(MDScreen):
    text = StringProperty()
    image = StringProperty()
    active = BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def build_chat(self):
        self.msg_builder(self.app.chat_id)
        # self.chat_screen.text = profile['name']
        # self.chat_screen.image = profile['image']
        # self.chat_screen.active = profile['active']
        # self.wm.switch_to(self.chat_screen)

    def msg_builder(self, profile):
        '''Create a message bubble for creating chat.'''
        # for prof in profile['msg']:
        #     for messages in prof.split("~"):
        #         if messages != "":
        #             message, time, isRead, sender = messages.split(";")
        #             self.chatmsg = ChatBubble()
        #             self.chatmsg.msg = message
        #             self.chatmsg.time = time
        #             self.chatmsg.isRead = isRead
        #             self.chatmsg.sender = sender
        #             self.ids['msglist'].add_widget(self.chatmsg)
        #         else:
        #             print("No message")
        #
        #         print(self.chatmsg.isRead)

    def chat_list_builder(self):
        for profile in profiles:
            for message in profile['msg']:
                self.chatitem = ChatListItem()
                self.chatitem.profile = profile
                self.chatitem.friend_name = profile['name']
                self.chatitem.friend_avatar = profile['image']

                lastMessage, time, isRead, sender = message.split(';')
                self.chatitem.msgg = lastMessage
                self.chatitem.timestamp = time
                self.chatitem.isRead = isRead
            self.wm.screens[0].ids['chatTimeLine'].add_widget(self.chatitem)

    def groups(self):
        self.manager.current = 'groups'