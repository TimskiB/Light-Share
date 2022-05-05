import os
import time
import uuid

import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db

from dotenv import load_dotenv


class EventListener:
    def __init__(self):
        load_dotenv()
        self.api_endpoint = os.getenv("URL")
        self.rest_api_url = os.getenv("REST_API_URL")
        self.web_api_key = os.getenv("WEB_API_KEY")
        # Get the path to the firebase credentials file

        # cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        if len(firebase_admin._apps) == 0:
            print("[INFO] Initializing Firebase")
            cred_path = f'{os.getcwd()}/libs/backend/listeners/firebase-sdk.json'
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://lightshare-b528a-default-rtdb.europe-west1.firebasedatabase.app/'

            })
            time.sleep(0.5)
        self.users_ref = db.reference('/users')
        self.event_occ = False
        self.event = None

    def listen(self, app):
        self.user_id = app.user_id
        e = self.users_ref.child(self.user_id).child('events').listen(self.event_handler)
        while True:
            time.sleep(0.5)
            e.close()
            if self.event_occ:
                if self.event_info.event_type != "patch":
                    # print(f"\tDATA: {self.event.data} TYPE: {self.event.event_type}")
                    if data := self.find_event_key(app, self.event):
                        print("[INFO] Event received")
                        print(f"\tDATA: {self.event_info.data} TYPE: {self.event_info.event_type}")
                        return data, self.event[data]
                self.event_occ = False

            e = self.users_ref.child(self.user_id).child('events').listen(self.event_handler)

    def event_handler(self, event):
        time.sleep(0.5)
        self.event_info = event
        self.event = self.users_ref.child(self.user_id).child('events').get()
        # self.event = event
        self.event_occ = True

    def find_event_key(self, app, data):
        """
        Check if any key in data does not exist in self.app.events.
        """
        for key in data:
            if key not in app.events and key != "example" and data[key]["read"] == False:
                return key
        return False


def listen_for_events(app):
    listener = EventListener()

    return listener.listen(app)
