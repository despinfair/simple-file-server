import socket
import os
import mimetypes
import html
from urllib.parse import unquote

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", 1159))
server_socket.listen()

while True:
    connection, address = server_socket.accept()

    data = connection.recv(1024)
    print(data.decode())

    path = "/"
    paths = data.decode().split()
    if len(paths) > 1:
        path = unquote(paths[1])

    print(path)

    root = os.path.abspath("./content")
    file_path = os.path.abspath("./content" + path)

    if os.path.commonpath([root, file_path]) != root:
        connection.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
        connection.close()
        continue

    isdir_or_filenotexist = (os.path.isdir(file_path) or not os.path.exists(file_path)) and path != "/"

    if path == "/" or isdir_or_filenotexist:
        items = os.listdir(root)

        links = ""
        for item in items:
            safe_item = html.escape(item)
            links += f'<a href="/{safe_item}">{safe_item}</a><br>'

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>File Server</title>
        </head>
        <body>
            <h2>{"" if not isdir_or_filenotexist else f"{path[1::]} is directory or doesnt exist"}<h2>
            <h1>Files</h1>
            {links}
        </body>
        </html>
        """.encode("utf-8")

        connection.sendall(b"HTTP/1.1 200 OK\r\n")
        connection.sendall(b"Content-Type: text/html; charset=utf-8\r\n")
        connection.sendall(f"Content-Length: {len(body)}\r\n".encode())
        connection.sendall(b"\r\n")
        connection.sendall(body)
        connection.close()

    elif path == "/hello":

        body = "Привет от сервера".encode("utf-8")

        connection.sendall(b"HTTP/1.1 200 OK\r\n")
        connection.sendall(b"Content-Type: text/plain; charset=utf-8\r\n")
        connection.sendall(f"Content-Length: {len(body)}\r\n".encode())
        connection.sendall(b"\r\n")
        # connection.sendall(b"Hello from server")
        connection.sendall(body)
        connection.close()

    else:
        with open(root + path, "rb") as file:
            body = file.read()

        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        connection.sendall(b"HTTP/1.1 200 OK\r\n")
        connection.sendall(f"Content-Type: {content_type}\r\n".encode())
        connection.sendall(b"\r\n")
        connection.sendall(body)
        connection.close()

