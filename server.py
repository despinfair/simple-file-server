import socket
import os
import mimetypes
import html

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 1159))
server_socket.listen()

while True:
    connection, address = server_socket.accept()

    data = connection.recv(1024)
    print(data.decode())

    path = data.decode().split()[1]
    print(path)

    root = os.path.abspath("./content")
    file_path = os.path.abspath("./content" + path)

    if os.path.commonpath([root, file_path]) != root:
        connection.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
        connection.close()
        continue

    if path == "/":
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
        try:
            with open(root + path, "rb") as file:
                body = file.read()

            content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

            connection.sendall(b"HTTP/1.1 200 OK\r\n")
            connection.sendall(f"Content-Type: {content_type}\r\n".encode())
            connection.sendall(b"\r\n")
            connection.sendall(body)
            connection.close()

        except FileNotFoundError:
            connection.sendall(b"HTTP/1.1 404 Not Found\r\n")
            connection.close()