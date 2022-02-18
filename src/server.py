import socket
import os
import threading
import config

class Client:
    name = ""
    channel = "main"

    def __init__(self, name):
        self.name = name

def send_message_to_channel(clients, message, channel):
    message = message.encode(config.ENCODING)
    for client in clients:
        if (client.channel == channel):
            client.send(message)

def broadcast_message(clients, message):
    message = message.encode(config.ENCODING)
    for client in clients:
        client.send(message)

def send_message_to_client(clients, message_contents, sender):
    message_contents = message_contents.decode(config.ENCODING)
    recipient_name, message = message_contents.split(" ", 1)
    recipient_name = recipient_name.strip("@")

    for k, v in clients.items():
        if (v.name == recipient_name):
            k.send(f"{clients[sender]} -> {recipient_name}: {message}".encode(config.ENCODING))

def add_client_chat_formatting(client, message):
    return f"{client.name}: {message}"

def client_handler(connection, clients):
    connection.send(config.CHANGE_NICKNAME_CMD.encode(config.ENCODING))
    nickname = connection.recv(config.BUFFER_SIZE).decode(config.ENCODING)
    client = Client(nickname)
    connection.send(str.encode(f"Welcome to the server #{client.channel} channel"))
    broadcast_message(clients, f"[+] {client.name} has joined the server.")
    send_message_to_channel(clients, f"[+] {client.name} has joined the channel.", client.channel)
    clients[connection] = client

    while True:
        try:
            pass
            data = connection.recv(config.BUFFER_SIZE).decode(config.ENCODING)

            if (config.CHANGE_CHANNEL_CMD in data):
                print("Change channel")
            elif (config.CHANGE_NICKNAME_CMD in data):
                client.name = data.replace(config.CHANGE_NICKNAME_CMD + ';', '')
            else:
                send_message_to_channel(clients, add_client_chat_formatting(data), client.channel)
        except socket.error as e:
            print(f"[!] {e}")
            del clients[connection]
            broadcast_message(clients, f"[-] {client.name}: has left the server.")
            connection.close()
            break


def main():
    clients = {}
    channels = ["main"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = config.PORT

    try:
        server_socket.bind((host, port))
    except socket.error as e:
        print(f"[!] Unable to start server: {str(e)}")

    server_socket.listen()
    print(f"[*] Listening on {host}:{port}")

    while True:
        client, address = server_socket.accept()
        print(f"[+] {address} connected.")
        threading.Thread(target=client_handler, args=(client, clients)).start()

    server_socket.close()

thread = threading.Thread(target=main)
thread.start()
thread.join()
