# import modules
import socket
import threading
import time
import pickle

# make connection in the socket
host = socket.gethostbyname(socket.gethostname())
port = 9090

# starting the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# lists variables that'll store client's address and client's nicknames
clients = []
nicknames = []


# broadcast function to broadcast messages to all connected users
def broadcast(message):
    for client in clients:
        send_packet(client, message)


# function to send messages through the socket
def send_packet(client, message):
    message += "\n"
    message_enc = message.encode('ascii')
    print(f"Sending {message}")
    client.send(message_enc)


# Handle function to handle messages from clients
def handle(client):
    # using while true because we're going to use try and except
    # so if it's not as expected then it'll loop until the expected result obtained
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            print("packet", message)
            broadcast(message)
        except Exception as ex:
            print("Error", ex)
            # Removing and closing clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} has left the chat!")
            nicknames.remove(nickname)
            broadcastnicknames()
            break


# function to broadcast nicknames
def broadcastnicknames():
    time.sleep(1)
    joined = ';'.join(nicknames)
    msg = "NICKNAMES;" + joined
    broadcast(msg)


# receive function to receive connection and asks for client's name so that clients can go to next stage (chatting)
def receive():
    while True:
        # Accepting connection
        client, address = server.accept()
        while True:
            if client.recv(1024).decode('ascii') == 'USERLIST':
                client.send(pickle.dumps(nicknames))
                break
        print(f"Connected with {str(address)}!")
        # send request through the socket to ask the client for their nickname
        try:
            send_packet(client, 'NICK;')
            time.sleep(0.1)
            joined = ';'.join(nicknames)
            msg = 'USERLIST;' + joined
            send_packet(client, msg)
            nickname = client.recv(1024).decode('ascii')
            new_nick = 0
            for i in nicknames:
                if nickname == i:
                    new_nick = 1
            if new_nick != 1:
                nicknames.append(nickname)
                clients.append(client)

            # print and broadcast nicknames
            print(f"Nickname is {nickname}\n")
            broadcast(f"{nickname} Joined\n")
            send_packet(client, f"{nickname} connected to server\n")

            # Start Handling Thread for Clients
            thread = threading.Thread(target=handle, args=[client], )
            thread.start()

            broadcastnicknames()
        except:
            print('error')
        


print("Server running...")
receive()
