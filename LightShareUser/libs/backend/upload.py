import json
import os

import requests
from kivymd_extensions.akivymd.uix.progresswidget import AKCircularProgress

from LightShare.libs.backend.urls import BASE_URL
import mmap
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


def get_filename(path):
    """Find filename by path"""
    return os.path.basename(path).split('.')[0]


def prepare_files(path_list):
    """From the list of paths, prepare the files to be uploaded"""
    files_info = []
    for path in path_list:
        name = get_filename(path)
        info = {name: path, 'name': name}
        files_info.append(info)


def create_callback(encoder, loading_screen, loading_id):
    encoder_len = encoder.len
    # bar = ProgressBar(expected_size=encoder_len, filled_char='=')
    loading_screen.open()


    def callback(monitor):
        # bar.show(monitor.bytes_read)
        # loading_id.ids.progress_percent.current_percent = int(monitor.bytes_read / encoder_len * 100)
        loading_id.current_percent = int(monitor.bytes_read / encoder_len * 100)

    return callback


def create_upload():
    return MultipartEncoder({
        'form_field': 'value',
        'another_form_field': 'another value',
        'first_file': ('progress_bar.py', open(__file__, 'rb'), 'text/plain'),
        'second_file': ('progress_bar.py', open(__file__, 'rb'),
                        'text/plain'),
    })


def upload_content(upload_data, user_id, receiver_ids, device, loading_id, loading_screen, cloud_save=False):
    """Send POST request to upload text and files to the server"""
    url = f"{BASE_URL}/{user_id}/send"
    print("[UPLOAD] Uploading content to server...")
    # Open the file as a memory mapped string. Looks like a string, but
    # actually accesses the file behind the scenes.
    # file_info = prepare_files(upload_data["files"])
    # files = {'files[]': open(upload_data['files'][0], 'rb')}
    data = {
        "receiver_ids": receiver_ids,
        "cloud_save": cloud_save,
        "text": upload_data["text"],
        "device": device
    }
    # 'json': (None, json.dumps(data), 'application/json'),
    # files = {'files[]': (f'{get_filename(upload_data["files"][0])}', open(upload_data["files"][0], 'rb'))}

    ### GOOD VERSION ###
    files = {'json': json.dumps(data)}
    if upload_data["files"]:
        content = open(upload_data["files"][0], 'rb')
        files["files[]"] = content
    # content = open('C:\\Users\\timsk\\Downloads\\unknown.png', 'rb')
    print(f"[UPLOAD] Uploading data: {data}")
    r = requests.post(url, files=files)  # data=data


    ### TRY VERSION ###
    # files = {'json': json.dumps(data)}
    # if upload_data["files"]:
    #     content = open(upload_data["files"][0], 'rb')
    #     files["files[]"] = content
    # encoder = MultipartEncoder(files)
    # # encoder = create_upload()
    # callback = create_callback(encoder, loading_screen, loading_id)
    # monitor = MultipartEncoderMonitor(encoder, callback)
    # r = requests.post(url, data=monitor,
    #                   headers={'Content-Type': monitor.content_type})
    # print('\nUpload finished! (Returned status {0} {1})'.format(
    #     r.status_code, r.reason
    # ))
