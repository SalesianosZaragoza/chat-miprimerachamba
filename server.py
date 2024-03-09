from socket import *
import threading

server_ip = "localhost"
server_port = 9069

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)
print("Server listening on port", server_port)

clients = []

def handle_list_command(client_socket, clients):
    connected_clients = []
    print("Total clients connected:", len(clients))
    for client in clients:
        connected_clients.append(client[1])  # El nombre del cliente es el segundo elemento de la tupla
    print("Connected clients:", connected_clients)
    return connected_clients

def handle_private_message(client_socket, sender_name, recipient_name, message):
    for client in clients:
        if client[1] == recipient_name:
            private_message = f"\n[Private from {sender_name}]: {message}"
            client[0].send(private_message.encode())
            return
    client_socket.send("El usuario especificado no está conectado o no es válido.".encode())

def handle_client(client_socket, client_address, clients):
    print(f"Accepted connection from {client_address}")
    client_name = client_socket.recv(1024).decode()
    print(f"{client_name} has joined the chat")

    # Agregar el nombre del cliente a la lista de clientes
    clients.append((client_socket, client_name))

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            # El funcionamiento del /help
            if message.lower() == "/help":
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

            if message.lower() == "/exit":
                break

            if message.lower() == "/list":
                response = handle_list_command(client_socket, clients)
                client_socket.send("\n".join(response).encode())
            elif message.startswith("/msg"):
                parts = message.split(" ", 2)
                if len(parts) == 3:
                    recipient_name = parts[1]
                    private_message = parts[2]
                    handle_private_message(client_socket, client_name, recipient_name, private_message)
                else:
                    client_socket.send("Comando mal formado. Uso: /msg (usuario) (mensaje)".encode())
            else:
                # Send the received message to all other clients
                broadcast_message = f"\n{client_name}: {message}"
                print(broadcast_message)
                for client in clients:
                    if client[0] != client_socket:  # Compare sockets
                        client[0].send(broadcast_message.encode())

    except ConnectionResetError:
        print(f"Connection with {client_name} has been terminated.")
    
    print(f"{client_name} has left the chat")
    # Eliminar el cliente de la lista de clientes
    clients.remove((client_socket, client_name))
    client_socket.close()

while True:
    client_socket, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket, client_address, clients)).start() 