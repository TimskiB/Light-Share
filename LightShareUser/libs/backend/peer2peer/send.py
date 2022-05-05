import json
import os
import socket
from threading import Thread
import io

import tqdm

receivers = {}
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4  # 4KB


def get_filename(path):
    """Find filename by path"""
    return os.path.basename(path)  # .split('.')[0]


def send_local_content(host, port, connection, share_data):
    """ get the file size"""
    if share_data["text"] != "":
        pass
    if share_data["files"]:
        filesize = os.path.getsize(share_data["files"][0])  # TODO: multiple files support
        # create the client socket
        s = socket.socket()
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected.")

        # send the filename and filesize
        s.send(f"{get_filename(share_data['files'][0])}{SEPARATOR}{filesize}".encode())

        d = s.recv(10).decode()
        if d != "ACK":
            print("[ERROR] Failed to send the file name and size.")
            s.close()
            return
        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {get_filename(share_data['files'][0])}", unit="B",
                             unit_scale=True, unit_divisor=1024)
        with open(share_data['files'][0], "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the socket
        s.close()


def user_handler(user, user_id, user_name, share_data):
    addr = user["network_info"]
    print(f"[INFO] Requesting to send to {addr[0]}:{addr[1]}")
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((addr[0], addr[1]))
        if len(share_data["files"]) > 0:
            info = f"Containing: {len(share_data['files'])} files."
        else:
            info = "Containing: Text"
        connection.send(json.dumps({
            "header": "request_send",
            "user_id": user_id,
            "user_name": user_name,
            "info": info,
        }).encode("utf8"))
        if data := connection.recv(1024):
            data = json.loads(data.decode("utf8"))
            if data["header"] == "request_accept":
                receivers[user_id] = "Accept"
                send_local_content(addr[0], 9999, connection, share_data)
            if data["header"] == "request_reject":
                receivers[user_id] = "Reject"
                print("[INFO] Request rejected once.")
        else:
            receivers[user_id] = "Failed"
            print(f"[ERROR]No data received from {(addr[0], addr[1])}")
        connection.close()
    except Exception as e:
        receivers[user_id] = "Failed"
        print(f"\t[ERROR] Failed to find information about {(addr[0], addr[1])} ({e})")


def request_send(users_list, user_id, user_name, share_data):
    """
    Send a request to the user to send a share.
    """
    global receivers
    receivers = {}
    t_list = []
    for user in users_list:
        t = Thread(target=user_handler, args=(users_list[user], user_id, user_name, share_data))
        t.start()
        t_list.append(t)

    for t in t_list:
        t.join()


def receive_server(app_path):
    # device's IP address
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 9999
    # receive 4096 bytes each time
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    # create the server socket
    # TCP socket
    s = socket.socket()
    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    s.listen(5)
    print(f"[*] Listening for local content at {SERVER_HOST}:{SERVER_PORT}")
    # accept connection if there is any
    client_socket, address = s.accept()
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")

    # receive the file infos
    # receive using client socket, not server socket
    try:
        received = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[+] Received: {received}")
        filename, filesize = received.split(SEPARATOR)
        client_socket.send("ACK".encode())
        # remove absolute path if there is
        #filename, filesize = filename.decode(), filesize.decode()
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with io.open(f"uploads/{filename}", "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                #print(1)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                #print(f"[INFO] Received {len(bytes_read)} bytes.")

                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the client socket
        client_socket.close()
        # close the server socket
        s.close()
        return {
            "path": f"{app_path}\\uploads\\{filename}",
        }
    except Exception as e:
        print(f"[ERROR] Failed to receive file ({e})")
        return e
