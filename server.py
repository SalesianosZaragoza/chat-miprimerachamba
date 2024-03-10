from socket import *
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

def handle_list_command(client_socket, clients):
    connected_clients = []
    print("Total de clientes conectados: ", len(clients))
    for client in clients:
        connected_clients.append("\n\033[32m\u25CF\033[0m " + client[1])
        print("\033[32m\u25CF\033[0m", client[1])
    connected_clients_str = "".join(connected_clients)
    return connected_clients_str

def handle_private_message(client_socket, sender_name, recipient_name, message, clients):
    for client in clients:
        if client[1] == recipient_name:
            private_message = f"\n[Mensaje privado de {sender_name}]: {message}"
            client[0].send(private_message.encode())
            return
    client_socket.send("El usuario especificado no está conectado o no es válido.".encode())

def handle_name_command(client_socket, clients, old_name, new_name):
    for i, client in enumerate(clients):
        if client[1] == old_name:
            clients[i] = (client_socket, new_name)
            return f"Nombre cambiado de {old_name} a {new_name}"
    return "No se encontró el nombre de usuario especificado."

def handle_client(client_socket, client_address, clients):
    print(f"Conexion aceptada desde {client_address}")
    
    while True:
        client_name = client_socket.recv(1024).decode()
        
        if any(client[1] == client_name for client in clients):
            client_socket.send("El nombre de usuario ya está en uso. Por favor, elija otro nombre: ".encode())
        else:
            client_socket.send("OK".encode())  # Confirmar al cliente que se ha unido al chat
            break
    
    print(f"{client_name} se ha unido al chat")
    clients.append((client_socket, client_name))
    
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            if message.lower() == Commands.HELP.value:
                help_message = (
                    "-/list : Te muestra la lista de personas conectadas al server\n"
                    "-/create <nombrecanal> crea un canal\n"
                    "-/connect <nombrecanal> : conectarse a un canal\n"
                    "-/join <nombrecanal> : conectarse a un canal\n"
                    "-/msg <nombreusuario> para escribir por privado a una persona\n"
                    "-/quit <nombrecanal> para salir de un canal\n"
                    "-/name <nombre> : para cambiarse el nombre\n"
                    "-/kick <nombrecanal> <nombrepersona> para echar a alguien de un canal\n"
                    "-/exit : para salirse del chat programa\n"
                )
                client_socket.send(help_message.encode())

            if message.lower() in [Commands.EXIT.value, Commands.QUIT.value]:
                break

            if message.lower() == Commands.LIST.value:
                response = handle_list_command(client_socket, clients)
                client_socket.send(response.encode())
            if message.startswith(Commands.NAME.value):
                parts = message.split(" ", 1)
                if len(parts) == 2:
                    new_name = parts[1]
                    response = handle_name_command(client_socket, clients, client_name, new_name)
                    if response.startswith("Nombre cambiado"):
                        client_name = new_name
                    client_socket.send(response.encode())
                else:
                    client_socket.send("Comando mal formado. Usa: /name (nuevo_nombre)".encode())
            elif message.startswith(Commands.MSG.value):
                parts = message.split(" ", 2)
                if len(parts) == 3:
                    recipient_name = parts[1]
                    private_message = parts[2]
                    handle_private_message(client_socket, client_name, recipient_name, private_message, clients)
                else:
                    client_socket.send("Comando mal formado. Usa: /msg (usuario) (mensaje)".encode())
            else:
                broadcast_message = f"\n{client_name}: {message}"
                print(broadcast_message)
                for client in clients:
                    if client[0] != client_socket:
                        client[0].send(broadcast_message.encode())

    except ConnectionResetError:
        print(f"La conexión con {client_name} ha sido reiniciada por el cliente.")
    
    print(f"{client_name} ha abandonado el chat")
    clients.remove((client_socket, client_name))
    client_socket.close()

def main():
    server_ip = "192.168.1.44"
    server_port = 9069
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print("Server usa el puerto", server_port)
    clients = []

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address, clients)).start()

if __name__ == "__main__":
    main()