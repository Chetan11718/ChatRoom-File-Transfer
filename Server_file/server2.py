import socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 5050
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Server is listening on {host}")

usernames = []
clients = []
channels = {"default":[]}

#sends message to all clients
def broadcast(message, client_list=clients):
    for client in client_list:
        client.send(message.encode())

#switches client from channel1 to channel2
def switch_channel(client, username, ch1, ch2="default"):
    channels[ch1].remove(client)
    broadcast(f"{username} left...", channels[ch1])
    channels[ch2].append(client)
    client.send(f"\n\n***************** {ch2} *****************\n\n".encode())
    broadcast(f"{username} has joined {ch2}!", channels[ch2])

#disconnects client from the server
def disconnect(client, username, client_list):
    clients.remove(client)
    usernames.remove(username)
    client_list.remove(client)
    print(f"{username} has disconnected.")
    print(f"Client count: {threading.active_count() - 2}")
    broadcast(f"{username} has left...", client_list)
    client.close()

#receives new clients
def receive():
    while True:
        client, address = server.accept()
        if(client.recv(1024).decode()=="File_Transfer"):
            print(address)
            i=1
            f=open('file_'+str(i)+".pdf",'wb')
            i+=1
            l=client.recv(1024)
            while(l):
                f.write(l)
                l=client.recv(1024)
                if(l==""):
                    continue
            client.close()
            f.close()
        else:
            clients.append(client)
            channels["default"].append(client)
            client.send("username".encode())
            username = client.recv(1024).decode()
            usernames.append(username)
            print(f"New client: {username}, {address}")
            client.send(f"\n\n***************** default *****************\n\n".encode())
            broadcast(f"{username} has joined default!", channels["default"])
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
            print(f"Client count: {threading.active_count() - 1}")

#handles each individual client
def handle(client):
    client_list = channels["default"]
    index = clients.index(client)
    username = usernames[index]
    disconnected = False

    while True:
        try:
            message = client.recv(1024).decode()
            words = message.split()
            if words[1] == "disconnect":
                disconnected = True
                break
            elif words[1] == "join":
                channel = words[2]
                if client in channels["default"]:
                    curr_channel = "default"
                if channel not in channels.keys():
                    channels[channel] = []
                    print(f"New channel created: {channel}")
                switch_channel(client, username, curr_channel, channel)
                client_list = channels[channel]
                curr_channel = channel
            elif words[1] == "leave":
                switch_channel(client, username, channel)
                client_list = channels["default"]
            else:
                broadcast(message, client_list)
        except:
            disconnect(client, username, client_list)
            break

    if disconnected == True:
        client.send(f"\n\n****************************************\n\n".encode())
        client.send("disconnect".encode())
        disconnect(client, username, client_list)


receive()