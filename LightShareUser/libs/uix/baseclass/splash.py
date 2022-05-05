from kivymd.uix.screen import MDScreen


class SplashScreen(MDScreen):
    def on_enter(self):
        # self.title = self.ids.title_label
        # self.title.bind(size=self.title.setter("text_size"))
        #
        # self.description = self.ids.sub_title_label
        # self.description.bind(size=self.description.setter("text_size"))
        pass

    def login_screen(self):
        save = self.manager.transition
        self.manager.transition.duration = 1.3
        self.manager.current = "login"
        self.manager.transition = save
