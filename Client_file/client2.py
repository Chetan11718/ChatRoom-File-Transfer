import socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 5050
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
def chat():
    client.send("Chat".encode())
    username = input("Username: ")

    #receives messages from the server
    def receive():
        while True:
            try:
                message = client.recv(1024).decode()
                if message == "username":
                    client.send(username.encode())
                elif message == "disconnect":
                    break
                else:
                    print(message)
            except:
                print("An error occurred :(")
                client.close()
                break

    #sends messages to the server
    def write():
        while True:
            message = input()
            if message != "":
                client.send(f"{username}: {message}".encode())
            if message == "disconnect":
                break
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()

def transfer():
    client.send("File_Transfer".encode())
    f = open ("demo.pdf", "rb")
    l = f.read(1024)
    while (l):
        client.send(l)
        l = f.read(1024)
    client.close()

option=input("Enter CHAT to chat or TRAN to transfer files: ")
if(option=="CHAT"):
    chat()
elif(option=="TRAN"):
    transfer()
else:
    print("Enter valid option\n")
    