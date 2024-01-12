from socket import *

server_adress = "localhost"
server_port = 9069

#creating a new socket
server_socket = socket(AF_INET,SOCK_STREAM)
#
server_socket.bind((server_adress,server_port))
server_socket.listen()

while True:
    socket_conection, client_adress = server_socket.accept()
    print("conectado con un cliente. ",client_adress)
    while True:
        message = socket_conection.recv(1024).decode()
        print(message)

        if message == "exit":
            break
        #send the message to the client
        socket_conection.send(input().encode())
    print("desconectado con un cliente. ",client_adress)
    #close conection
    socket_conection.close()