from socket import *
import sys

server_ip = "localhost"
server_port = 9069

client_socket = socket(AF_INET,SOCK_STREAM)
client_socket.connect((server_ip,server_port))

while True:

    #write message
    message = input()
    if message != "exit":
        #send the message
        client_socket.send(message.encode())
        #recive the message
        response = client_socket.recv(1024).decode()
        print(response)

    else:
        client_socket.send(message.encode())
        #close conection
        client_socket.close()
        sys.exit()