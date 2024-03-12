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
    COLOR = "/color"

def handle_list_command(client_socket, channels, clients):
    channels_list = ["\033[36mCanales y clientes conectados:\033[0m"]
    for channel, members in channels.items():
        channel_info = f"\n\033[36m\u25CF\033[0m \033[36m{channel}:\033[0m"
        for member in members:
            for client_socket, client_name in clients:
                if client_name == member:
                    channel_info += f"\n  \033[32m\u25CF\033[0m {client_name}"
        channels_list.append(channel_info)
    channels_list_str = "".join(channels_list) + "\n"
    return channels_list_str

def handle_msg_command(client_socket, sender_name, recipient_name, message, clients):
    for client in clients:
        if client[1] == recipient_name:
            private_message = f"[Mensaje privado de {sender_name}]: {message}"
            client[0].send(private_message.encode())
            return
    client_socket.send("El usuario especificado no está conectado o no es válido.".encode())

def handle_name_command(client_socket, clients, old_name, new_name): # si uso /name en un canal, no me deja enviar mensajes hasta que me cambie de canal
    for i, client in enumerate(clients):
        if client[1] == old_name:
            clients[i] = (client_socket, new_name)
            return f"Nombre cambiado de {old_name} a {new_name}"
    return "No se encontró el nombre de usuario especificado."

def handle_color_command(client_socket, clients, client_name, color):
    for i, client in enumerate(clients):
        if client[1] == client_name:
            clients[i] = (client_socket, client_name, color)
            return f"Color cambiado a {color}"
    return "No se encontró el nombre de usuario especificado."

def handle_help_command(client_socket):
    help_message = (
                    "-/list : Te muestra la lista de personas conectadas al server y la lista de canales creados\n"
                    "-/create <nombrecanal> crea un canal\n"
                    "-/join <nombrecanal> : conectarse a un canal\n"
                    "-/msg <nombreusuario> para escribir por privado a una persona\n"
                    "-/quit <nombrecanal> para salir de un canal al general\n"
                    "-/name <nombre> : para cambiarse el nombre\n"
                    "-/kick <nombrecanal> <nombrepersona> para echar a alguien de un canal\n"
                    "-/exit : para salirse del chat programa\n"
                )
    client_socket.send(help_message.encode())
    

def handle_create_command(client_socket, channel_name, channels, client_name):
    for channel, members in channels.items():
        if client_name in members:
            members.remove(client_name)
    if channel_name not in channels:
        channels[channel_name] = [client_name]
        return f"Canal '{channel_name}' creado. Te has unido al canal '{channel_name}'.\n"
    else:
        return "El canal ya existe."


def handle_join_command(client_socket, channel_name, channels, client_name):
    if channel_name in channels:
        if client_name not in channels[channel_name]:
            for channel, members in channels.items():
                if client_name in members:
                    members.remove(client_name)
            channels[channel_name].append(client_name)
            return f"Te has unido al canal '{channel_name}'."
        else:
            return f"Ya estás en el canal '{channel_name}'."
    else:
        return "El canal especificado no existe."

def handle_quit_command(client_socket, channels, client_name):
    if client_name in channels["general"]:
        return "No puedes salir del canal general usando /quit. Usa /exit para salir del chat."
    else:
        for channel, members in channels.items():
            if client_name in members:
                members.remove(client_name)
        channels["general"].append(client_name)
        return f"Has abandonado tu canal, has sido redirigido al canal general.\n"

def handle_client(client_socket, client_address, clients, channels):
    print(f"Conexion aceptada desde {client_address}")
    client_name = client_socket.recv(1024).decode()
    print(f"{client_name} se ha unido al chat")
    clients.append((client_socket, client_name))
    
    if "general" not in channels:
        channels["general"] = []
    channels["general"].append(client_name)

    welcome_message = "¡Bienvenido al canal general! Crea o unete a otro canal mediante /create <n> o /join <n>.\n"
    client_socket.send(welcome_message.encode())
    
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            if message.lower() == Commands.HELP.value:
                handle_help_command(client_socket)
                
            elif message.lower() in [Commands.EXIT.value]:
                break
            
            elif message.lower() == Commands.QUIT.value:
                response = handle_quit_command(client_socket, channels, client_name)
                client_socket.send(response.encode())
                
            if message.lower() == Commands.LIST.value:
                response = handle_list_command(client_socket, channels, clients)
                client_socket.send(response.encode())
                
            if message.startswith(Commands.NAME.value):
                parts = message.split(" ", 1)
                if len(parts) == 2:
                    new_name = parts[1]
                    response = handle_name_command(client_socket, clients, client_name, new_name)
                    client_name = new_name
                    client_socket.send(response.encode())
                else:
                    client_socket.send("Comando mal formado. Usa: /name (nuevo_nombre)".encode())
                    
            elif message.startswith(Commands.MSG.value):
                parts = message.split(" ", 2)
                if len(parts) == 3:
                    recipient_name = parts[1]
                    private_message = parts[2]
                    handle_msg_command(client_socket, client_name, recipient_name, private_message, clients)
                else:
                    client_socket.send("Comando mal formado. Usa: /msg (usuario) (mensaje)".encode())
                    
            elif message.lower().startswith(Commands.CREATE.value):
                parts = message.split(" ", 1)
                if len(parts) == 2:
                    channel_name = parts[1]
                    response = handle_create_command(client_socket, channel_name, channels, client_name)
                    client_socket.send(response.encode())
                else:
                    client_socket.send("Comando mal formado. Usa: /create (nombre_canal)".encode())

            elif message.lower().startswith(Commands.JOIN.value):
                parts = message.split(" ", 1)
                if len(parts) == 2:
                    channel_name = parts[1]
                    response = handle_join_command(client_socket, channel_name, channels, client_name)
                    client_socket.send(response.encode())
                else:
                    client_socket.send("Comando mal formado. Usa: /join (nombre_canal)".encode())
                    
            else:
                broadcast_message = f"{client_name}: {message}"
                print(broadcast_message)
                for channel, members in channels.items():
                    if client_name in members:
                        for member_socket, member_name in clients:
                            if member_name in members:
                                member_socket.send(broadcast_message.encode())

    except ConnectionResetError:
        print(f"La conexión con {client_name} ha sido reiniciada por el cliente.")
    
    print(f"{client_name} ha abandonado el chat")
    clients.remove((client_socket, client_name))
    for channel, members in channels.items():
        if client_name in members:
            for member_socket, member_name in clients:
                if member_name in members and member_socket != client_socket:
                    member_socket.send(broadcast_message.encode())
    client_socket.close()

def main():
    server_ip = "192.168.1.44"
    server_port = 9069
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print("Server usa el puerto", server_port)
    clients = []
    channels = {}

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address, clients, channels)).start()

if __name__ == "__main__":
    main()