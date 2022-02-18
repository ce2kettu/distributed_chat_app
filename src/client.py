import socket
import config
import threading

def menu():
    print("Available options:")
    print("1) Create a channel")
    print("2) Join a channel")
    print("3) Send a private message")
    print("4) Connect to a server")
    print("5) Disconnect from the server")
    print("6) Exit")

    try:
        return int(input("Your choice: "))
    except ValueError:
        return -1;

def query_server_address():
    return input("Enter server IP address: ")

def establish_server_connection(host):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting to the server...")
    try:
        conn.connect((host, config.PORT))
        return conn
    except socket.error:
        return None

def update_connection_status(socket):
    if (socket == None):
        print("Connection failed.")
        return False
    else:
        print("Connection successful.")
        return True

def create_messaging_thread(socket):
        threading.Thread(target=server_handler, args=(socket,)).start()

def server_handler(socket):
    while True:
        try:
            data = socket.recv(config.BUFFER_SIZE).decode(config.ENCODING)
            if (data == config.CHANGE_NICKNAME_CMD):
                socket.send(nickname.encode(config.ENCODING))
            else:
                print(data)
        except socket.error as e:
            print(f"[!] {e}")
            print("Closed connection due to an error.")
            socket.close()
            break

if __name__ == "__main__":
    nickname = input("Enter your nickname: ")
    host = query_server_address()
    socket = establish_server_connection(host)
    isConnected = update_connection_status(socket)

    if (isConnected):
        create_messaging_thread(socket)

    while True:
        choice = menu()
        print()

        match choice:
            case 1:
                print("hey")
            case 2:
                print("hey")
            case 3:
                print("hey")
            case 4:
                if not isConnected:
                    host = query_server_address()
                    socket = establish_server_connection(host)
                    isConnected = update_connection_status(socket)

                    if (isConnected):
                        create_messaging_thread(socket)
                else:
                    print("Already connected to a server.")
            case 5:
                if isConnected:
                    socket.close()
                    print("Disconnected from the server.")
                else:
                    print("Not connected to a server.")
            case 6:
                print("Exiting...")
                break
            case _:
                print("Invalid option")

