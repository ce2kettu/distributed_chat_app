import socket
import config
import threading


class ClientApp:
    def __init__(self, nickname, host):
        self.nickname = nickname
        self.host = host
        self.isConnected = False
        self.socket = None
        self.runThreads = True

    def establish_server_connection(self):
        if (self.isConnected):
            return

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to the server...")
        try:
            self.socket.connect((self.host, config.PORT))
            print("Connected.")
            self.isConnected = True
        except socket.error:
            print("Could not connect to the server.")
            self.isConnected = False

    def create_messaging_thread(self):
        if (self.isConnected):
            threading.Thread(target=self.server_handler, args=()).start()

    def connect(self):
        if (not self.isConnected):
            self.runThreads = True
            app.establish_server_connection()
            app.create_messaging_thread()

    def disconnect(self):
        if (self.isConnected):
            self.isConnected = False
            self.runThreads = False
            self.socket.close()

    def send_packet(self, value):
        if (self.isConnected):
            self.socket.send(value.encode(config.ENCODING))

    def send_command(self, params):
        self.send_packet(";".join(params))

    def send_message(self, message):
        self.send_packet(message)

    def create_channel(self, channelName):
        self.send_command([config.CREATE_CHANNEL_CMD, channelName])

    def join_channel(self, channelName):
        self.send_command([config.JOIN_CHANNEL_CMD, channelName])

    def direct_message(self, contents):
        parts = contents.split(" ")

        if (len(parts) > 1):
            targetUser = parts[0]
            message = " ".join(parts[1:])
            self.send_command([config.DIRECT_MESSAGE_CMD, targetUser, message])
        else:
            print("Usage: !pm [user] [message]")

    def change_name(self, newName):
        newName = config.format_string(newName)
        self.send_command([config.CHANGE_NICKNAME_CMD, newName])
        self.nickname = newName

    def server_handler(self):
        while self.runThreads:
            try:
                data = self.socket.recv(
                    config.BUFFER_SIZE).decode(config.ENCODING)
                if (data == config.CHANGE_NICKNAME_CMD):
                    self.socket.send(self.nickname.encode(config.ENCODING))
                else:
                    print(data, end="")
            except socket.error as e:
                print("Disconnected from the server.")
                self.socket.close()
                self.isConnected = False
                break


def help_menu():
    print("Available commands:")
    print("!disconnect")
    print("!connect")
    print("!changename")
    print("!pm [user] [message]")
    print("!join [channel name]")
    print("!create [channel name]")
    print("!exit")
    print("!help")


def query_server_address():
    return input("Enter server IP address: ")


# parse command from input if exists - e.g., !join [channel]
def parse_command(value):
    cmd = ("chat", value)

    if (len(value) > 0 and value[0] == "!"):
        value = value[1:]
        parts = value.split(" ")

        if (len(parts) > 0):
            command = parts[0]
            contents = " ".join(parts[1:])
            cmd = (command, contents)

    return cmd


if __name__ == "__main__":
    help_menu()
    nickname = config.format_string(input("Enter your nickname: "))
    host = query_server_address()
    app = ClientApp(nickname, host)
    app.connect()

    try:
        while True:
            (command, contents) = parse_command(input())

            match command:
                case "chat":
                    app.send_message(contents)
                case "connect":
                    if (not app.isConnected):
                        host = query_server_address()
                        app.host = host
                        app.connect()
                    else:
                        print("Already connected to a server.")
                case "disconnect":
                    if (app.isConnected):
                        app.disconnect()
                    else:
                        print("Not connected to a server.")
                case "create":
                    app.create_channel(contents)
                case "join":
                    app.join_channel(contents)
                case "pm":
                    app.direct_message(contents)
                case "changename":
                    app.change_name(contents)
                case "help":
                    help_menu()
                case "exit":
                    print("Exiting...")
                    app.disconnect()
                    break
                case _:
                    print("Invalid option")
    except KeyboardInterrupt:
        app.disconnect()
        print("[i] Exiting...")
