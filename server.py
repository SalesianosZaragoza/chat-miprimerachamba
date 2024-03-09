from socket import *
import threading
from commands import handle_commands

server_ip = "localhost"
server_port = 9069

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)
print("Server listening on port", server_port)

clients = []

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

            if message.lower() == "/exit":
                break

            if message.startswith("/"):
                response = handle_commands(message, client_socket, clients)
                if response:
                    client_socket.send(response.encode())  # Send response to the client
            else:
                # Send the received message to all other clients
                broadcast_message = f"{client_name}: {message}"
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
