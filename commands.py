def handle_list_command(client_socket, clients):
    connected_clients = []
    print("Total clients connected:", len(clients))
    for client in clients:
        connected_clients.append(client[1])  # El nombre del cliente es el segundo elemento de la tupla
    print("Connected clients:", connected_clients)
    return connected_clients

def handle_commands(message, client_socket, clients):
    if message.lower() == "/list":
        print("llega")
        return "\n".join(handle_list_command(client_socket, clients))  # Convert list to string
    else:
        print(f"Command not found: {message}")
