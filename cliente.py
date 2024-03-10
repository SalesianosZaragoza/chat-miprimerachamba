from socket import *
import sys
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Conexión perdida con el servidor.")
                break
            if message.lower().startswith("/help"):
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
        if user_message.lower().startswith("/msg"):
            parts = user_message.split(" ", 2)
            if len(parts) == 3:
                recipient_name = parts[1]
                private_message = parts[2]
                user_message = f"/msg {recipient_name} {private_message}"
            else:
                print("Comando mal formado. Uso: /msg (usuario) (mensaje)")
                continue
        if user_message.lower().startswith("/name"):
            parts = user_message.split(" ", 1)
            if len(parts) == 2:
                new_name = parts[1]
                user_message = f"/name {new_name}"
                client_name = new_name
            else:
                print("Comando mal formado. Uso: /name (nuevo_nombre)")
                continue
        
        client_socket.send(user_message.encode())

        if user_message.lower() in ["/exit", "/quit"]:
            client_socket.close()
            receive_thread.join()
            print("Has salido del chat.")
            break

if __name__ == "__main__":
    main()
