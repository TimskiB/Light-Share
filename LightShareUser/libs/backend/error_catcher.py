import os
import sys


def error_info():
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    except Exception as e:
        print(f"[CRITICAL] Could not get error info: {e}")