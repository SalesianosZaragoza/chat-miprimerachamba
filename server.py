from socket import *
import threading

server_ip = "localhost"
server_port = 9069

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)
print("Server listening on port", server_port)

clients = []

def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    client_name = client_socket.recv(1024).decode()
    print(f"{client_name} has joined the chat")

    while True:
        message = client_socket.recv(1024).decode()
        if message == "exit" or not message:
            print(f"{client_name} has left the chat")
            clients.remove(client_socket)
            client_socket.close()
            break
        print(f"{client_name}: {message}")
        for client in clients:
            if client != client_socket:
                client.send(message.encode())

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()