from socket import *
import sys
from commands import handle_commands

def main():
    server_ip = "localhost"
    server_port = 9069
    client_name = input("Ingrese su nombre: ")

    # Crear el socket del cliente
    client_socket = socket(AF_INET, SOCK_STREAM)
    
    # Conectar al servidor
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print("Error al conectar al servidor:", e)
        sys.exit(1)

    # Enviar el nombre del cliente al servidor
    client_socket.send(client_name.encode())

    while True:
        # Leer el mensaje del usuario
        message = input("Ingrese su mensaje: ")

        # Enviar el mensaje al servidor
        client_socket.send(message.encode())

        # Verificar si el usuario quiere salir del chat
        if message.lower() == "/exit":
            client_socket.close()
            sys.exit("Has salido del chat.")

        # Esperar la respuesta del servidor y manejar los comandos
        response = handle_commands(message, client_socket, [])

        # Imprimir la respuesta del servidor
        if response:
            print(response)

if __name__ == "__main__":
    main()