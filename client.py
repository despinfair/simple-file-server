import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 1159))


client_socket.sendall(b"Hello ")

while True:
    data = client_socket.recv(1024)
    if len(data) == 0:
        break
    print(data.decode())