from socket import *
import sys
import threading
from enum import Enum

class Commands(Enum):
    LIST = "/list"
    HELP = "/help"
    CREATE = "/create"
    CONNECT = "/connect"
    JOIN = "/join"
    MSG = "/msg"
    QUIT = "/quit"
    NAME = "/name"
    KICK = "/kick"
    EXIT = "/exit"

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Conexión perdida con el servidor.")
                break
            if message.lower().startswith(Commands.HELP.value):
                continue
            print(message)
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
        except ConnectionAbortedError:
            print("")
            break

def main():
    server_ip = "localhost"
    server_port = 9069
    client_name = input("Ingrese su nombre: ")
    client_socket = socket(AF_INET, SOCK_STREAM)
    
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print("Error al conectar al servidor:", e)
        sys.exit(1)

    client_socket.send(client_name.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        user_message = input(f"\n{client_name}: ")
        if user_message.lower().startswith(Commands.MSG.value):
            parts = user_message.split(" ", 2)
            if len(parts) == 3:
                recipient_name = parts[1]
                private_message = parts[2]
                user_message = f"{Commands.MSG.value} {recipient_name} {private_message}"
            else:
                print("Comando mal formado. Uso: /msg (usuario) (mensaje)")
                continue
        if user_message.lower().startswith(Commands.NAME.value):
            parts = user_message.split(" ", 1)
            if len(parts) == 2:
                new_name = parts[1]
                user_message = f"{Commands.NAME.value} {new_name}"
                client_name = new_name
            else:
                print("Comando mal formado. Uso: /name (nuevo_nombre)")
                continue
        
        client_socket.send(user_message.encode())

        if user_message.lower() in [Commands.EXIT.value, Commands.QUIT.value]:
            client_socket.close()
            receive_thread.join()
            print("Has salido del chat.")
            break

if __name__ == "__main__":
    main()