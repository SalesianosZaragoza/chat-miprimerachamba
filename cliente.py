from socket import *
import sys
import threading
import select

def receive_messages(client_socket):
    while True:
        try:
            # Leer el mensaje del servidor
            message = client_socket.recv(1024).decode()
            if not message:
                print("Conexión perdida con el servidor.")
                break
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

    # Iniciar un hilo para recibir mensajes del servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        # Leer el mensaje del usuario
        user_message = input(f"\n{client_name}: ")

        # Enviar el mensaje al servidor
        client_socket.send(user_message.encode())

        # Verificar si el usuario quiere salir del chat
        if user_message.lower() == "/exit":
            client_socket.close()
            # Esperar a que el hilo de recepción termine antes de salir
            receive_thread.join()
            print("Has salido del chat.")
            break

if __name__ == "__main__":
    main()
 