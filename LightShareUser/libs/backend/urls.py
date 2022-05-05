import os

from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("URL")
GET_USER_INFO = f"{BASE_URL}/user/info"