from rpcContentServer import RPCContentServer
import pathlib
import streamlit as st
from io import StringIO
import os
import pandas as pd
import socket
from io import StringIO
import json
import threading
#import public_ip as ip


HEADER = 64
PORT = 5055
# SERVER = ""
# Another way to get the local IP address automatically
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
print(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'UTF-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


if 'serverUp' not in st.session_state:
    st.session_state['serverUp'] = 'false'


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
        conn.send("Msg received".encode(FORMAT))

    conn.close()

@st.cache_resource
def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def register_server(serverName,serverIP,serverPort):
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    server.register_server(serverName,serverIP,serverPort)
    server.disconnect()
    return st.success("Content Provider Info registed with the server")

def get_serverList():
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    st.write(server.get_serverList())
    server.disconnect()
    return 'Completed'
    
    

if st.session_state['serverUp'] == 'false':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    st.session_state['serverUp'] = 'true'
    threading.Thread(target=start).start()
    register_server(1,SERVER,PORT)
    



def save_uploadedfile(fileContent,fileName,platformName,ipAddress):
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    server.upload_file(fileContent,fileName,platformName,ipAddress)
    server.disconnect()
    return st.success("File registed with the server")

st.write(get_serverList())

platform = st.selectbox(
    'Please select the Subject for which you want to update the content',
    ('DC', 'CSIS', 'SF', 'DW'))

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To convert to a string based IO:
    fileContent = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    st.write(fileContent)
    fileName = uploaded_file.name
    st.write(fileName)
    ipAddress = str(socket.gethostbyname(socket.gethostname()))
    st.write(ipAddress)
    #file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
    save_uploadedfile(fileContent,fileName,platform,ipAddress)
    

