from kivy.animation import Animation
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivymd.uix.behaviors import HoverBehavior


class HoverButton(Button, HoverBehavior):
    background = ListProperty((71/255, 104/255, 237/255, 1))
    def on_enter(self):
        self.background = (251/255, 104/255, 23/255, 1)
        Animation(size_hint=(.6, .1), d=0.2).start(self)

    def on_leave(self):
        self.background = (71/255, 104/255, 237/255, 1)
        Animation(size_hint=(.5, .09), d=0.2).start(self)