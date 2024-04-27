import socket
import threading
from rpcContentServer import RPCContentServer
import pandas as pd
import json
import numpy

HEADER = 64
PORT = 5050
# SERVER = ""
# Another way to get the local IP address automatically
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
print(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'UTF-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
df_serverList = pd.DataFrame()
no_of_sites = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def register_server(serverName,serverIP,serverPort):
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    server.register_server(serverName,serverIP,serverPort)
    server.disconnect()
    print("Content Provider Info registed with the server")
    return "Completed"


def get_serverList():
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    serv_list = server.get_serverList()
    print(serv_list)
    server.disconnect()
    return serv_list

def initialize_tokens():
    global initial_seq 
    initial_seq = 0
    serv_list = (get_serverList())
    y = json.loads(serv_list)
    df_serverList = pd.DataFrame(y)
    df_serverList = df_serverList.rename(columns={'0': 'ServerName', '1': 'ServerIP', '2': 'ServerPort'})
    print(df_serverList)
    no_of_sites = len(df_serverList.index)
    global request_array
    request_array = [0] * no_of_sites
    global token_array
    token_array = [0] * no_of_sites
    global token_queue
    token_queue = []
    #token_queue.append('a')
    print(request_array)
    print(token_array)
    #print(token_queue[0])
    #token_queue.pop(0)
    print(token_queue)
    return 'Initialized'


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(msg)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            elif msg == 'INIT':
                initialize_tokens()
            print(f"[{addr}] {msg}")
        conn.send("Initialization Completed".encode(FORMAT))

    conn.close()


def start():
    register_server('1',SERVER,str(PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        


print("[STARTING] Content server is starting...")
start()