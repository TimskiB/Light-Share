import certifi


def create_error(req, result):
    print(f"[ERROR] Create device: {result}")


def on_device_error(req, result):
    print(f"[ERROR] Device error: {result}")
