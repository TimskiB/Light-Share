import os
import sys

import requests
from dotenv import load_dotenv

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from LightShare.libs.backend.error_catcher import error_info


def current_datetime():
    """Find current data and time and return it as a string"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# def override_where():
#     """ overrides certifi.core.where to return actual location of cacert.pem"""
#     # change this to match the location of cacert.pem
#     print(os.path.join(os.getcwd(), 'libs', 'backend', 'certificate.pem'))
#     return os.path.join(os.getcwd(), 'libs', 'backend', 'certificate.pem')
#
#
# # is the program compiled?
# if hasattr(sys, "frozen"):
#     import certifi.core
#
#     os.environ["REQUESTS_CA_BUNDLE"] = override_where()
#     certifi.core.where = override_where
#
#     # delay importing until after where() has been replaced
#     import requests.utils
#     import requests.adapters
#
#     # replace these variables in case these modules were
#     # imported before we replaced certifi.core.where
#     requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
#     requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()


class Auth:
    def __init__(self):
        load_dotenv()
        self.api_endpoint = os.getenv("URL")
        hasattr(sys, "frozen")

    def email_sign_up(self, email, password, display_name):
        try:
            print(f"[HTTP] {self.api_endpoint}/user/signup")
            response = requests.post(f'{self.api_endpoint}/user/signup', json={
                "email": email,
                "password": password,
                "display_name": display_name
            })
            return response.json() if response.status_code == 201 else None

        except Exception as e:
            print(f"[ERROR] Sign up error:\n\t{error_info()}")
            return None

    def email_sign_in(self, email, password):
        # try:
        #     user = auth.sign_in
        #     self.users_ref.child(user.uid).update({
        #         'last_login': current_datetime()
        #     })
        #     return user.uid
        #
        # except Exception as e:
        #     print(f"[ERROR] Sign in error:\n\t{error_info()}")
        #     return None

        return self.post_json(f"{self.api_endpoint}/user/signin",
                              {
                                  "email": email,
                                  "password": password,
                              })

    def post_json(self, url, json):
        try:

            print(f"[POST] {url}")
            path = os.path.join(os.getcwd(), 'libs', 'backend', 'ca_bundle.crt')
            response = requests.post(url, json=json, verify=False)  #TODO: verify=False
            return response.json() if response.status_code == 201 else None

        except Exception as e:
            print(f"[ERROR] {url} Failed:\n\t{error_info()}")
            return None
