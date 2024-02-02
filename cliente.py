from socket import *
import sys

server_ip = "localhost"
server_port = 9069
client_name = input("Ingrese su nombre: ")

client_socket = socket(AF_INET,SOCK_STREAM)
client_socket.connect((server_ip,server_port))

client_socket.send(client_name.encode())

while True:

    #write message
    message = input("Pon tu mensaje :")
    if message != "exit":
        #send the message
        client_socket.send(f" {message}".encode())
        #recive the message
        response = client_socket.recv(1024).decode()
        print("SERVER :"+str(response))

    else:
        client_socket.send(message.encode())
        #close conection
        client_socket.close()
        sys.exit()