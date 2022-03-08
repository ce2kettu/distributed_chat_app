import socket
import threading
import config


class Client:
    def __init__(self, name):
        self.name = name
        self.channel = "main"


class ServerApp:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = config.PORT
        self.clients = {}
        self.channels = ["main"]
        self.isRunning = False

    def start(self):
        if (self.isRunning):
            return

        try:
            self.isRunning = True
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"[*] Listening on {self.host}:{self.port}")
        except socket.error as e:
            print(f"[!] Unable to start server: {str(e)}")

    # append a new line character and the encode message
    # before sending it to a client
    def apply_message_preprocessing(self, message):
        return (message + "\n").encode(config.ENCODING)

    def send_message_to_channel(self, message, channel):
        message = self.apply_message_preprocessing(message)
        for k, v in self.clients.items():
            if (v.channel == channel):
                k.send(message)

    def broadcast_message(self, message):
        message = self.apply_message_preprocessing(message)
        for client in self.clients:
            client.send(message)

    def send_message_to_client(self, client, message):
        message = self.apply_message_preprocessing(message)
        client.send(message)

    def handle_direct_message(self, message, recipientName, sender, senderConnection):
        isRecipientFound = False
        for k, v in self.clients.items():
            if (v.name == recipientName):
                isRecipientFound = True
                self.send_message_to_client(senderConnection, f"You -> {recipientName}: {message}")
                self.send_message_to_client(k, f"{sender.name} -> {recipientName}: {message}")
        
        if (not isRecipientFound):
            self.send_message_to_client(senderConnection, "[e] Recipient not found")

    def add_client_chat_formatting(self, client, message):
        return f"{client.name}: {message}"

    def new_client_thread(self, client, address):
        threading.Thread(target=self.client_handler, args=(client, address)).start()

    def does_channel_exist(self, value):
        for channel in self.channels:
            if (channel == value):
                return True
        return False

    def client_handler(self, connection, address):
        # ask nickname
        connection.send(config.CHANGE_NICKNAME_CMD.encode(config.ENCODING))
        nickname = connection.recv(config.BUFFER_SIZE).decode(config.ENCODING)
    
        client = Client(nickname)
        client.address = address
        self.clients[connection] = client
        self.send_message_to_client(
            connection, f"Welcome to the server's #{client.channel} channel")
        self.broadcast_message(f"[+] {client.name} has joined the server.")
        self.send_message_to_channel(
            f"[+] {client.name} has joined the channel.", client.channel)

        while self.isRunning:
            try:
                data = connection.recv(
                    config.BUFFER_SIZE).decode(config.ENCODING)

                if (config.CHANGE_NICKNAME_CMD in data):
                    parts = data.split(";")
                    if (len(parts) == 2):
                        oldName = client.name
                        client.name = parts[1]
                        self.send_message_to_client(connection, f"[i] Name changed from '{oldName}' to '{client.name}'")
                    else:
                        self.send_message_to_client(connection, "[e] Invalid command")
                elif (config.CREATE_CHANNEL_CMD in data):
                    parts = data.split(";")
                    if (len(parts) == 2):
                        channelName = parts[1]
                        if (self.does_channel_exist(channelName)):
                            self.send_message_to_client(connection, "[e] Channel already exists")
                        else:
                            self.channels.append(channelName)
                            self.send_message_to_client(connection, f"[i] Created channel '{channelName}'")
                    else:
                        self.send_message_to_client(connection, "[e] Invalid command")
                elif (config.JOIN_CHANNEL_CMD in data):
                    parts = data.split(";")
                    if (len(parts) == 2):
                        channelName = parts[1]
                        if (client.channel == channelName):
                            self.send_message_to_client(connection, "[e] Already in this channel")
                        elif (self.does_channel_exist(channelName)):
                            self.send_message_to_channel(
                                f"[-] {client.name} has left the channel.", client.channel)
                            client.channel = channelName
                            self.send_message_to_channel(
                                f"[+] {client.name} has joined the channel.", client.channel)
                        else:
                            self.send_message_to_client(connection, "[e] Channel does not exist")
                    else:
                        self.send_message_to_client(connection, "[e] Invalid command")
                elif (config.DIRECT_MESSAGE_CMD in data):
                    parts = data.split(";")
                    if (len(parts) == 3):
                        recipientName = parts[1]
                        message = parts[2]
                        self.handle_direct_message(
                            message, recipientName, client, connection)
                    else:
                        self.send_message_to_client(connection, "[e] Invalid command")
                else:
                    self.send_message_to_channel(
                        self.add_client_chat_formatting(client, data), client.channel)
            except socket.error as e:
                print(f"[-] {client.address} disconnected.")
                del self.clients[connection]
                self.send_message_to_channel(
                    f"[-] {client.name} has left the channel.", client.channel)
                self.broadcast_message(
                    f"[-] {client.name} has left the server.")
                connection.close()
                break

    def stop(self):
        self.isRunning = False
        self.socket.close()


if __name__ == "__main__":
    app = ServerApp()
    app.start()

    try:
        while True:
            client, address = app.socket.accept()
            print(f"[+] {address} connected.")
            app.new_client_thread(client, address)
    except KeyboardInterrupt:
        app.stop()
        print("[i] Exiting...")

