from rpcContentServer import RPCContentServer
from rpcClient import RPCClient
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
from rpcServer import RPCServer

st.set_page_config(layout="wide")



if 'temp_serverUp' not in os.environ:
    os.environ['temp_serverUp'] = 'false'


def init_contentServer():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 5052)
    server.connect()
    st.write(server.initialize_requestArray())
    server.disconnect()
    return st.success("Content Provider Token Initialization")
    
def init_register_contentServer():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 5052)
    server.connect()
    st.write(server.register_server())
    server.disconnect()
    return st.success("Content Server Registered")

def request_criticalSection():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 5052)
    server.connect()
    msg = str(server.request_cs())
    server.disconnect()
    return msg



def release_criticalSection():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 5052)
    server.connect()
    st.write(server.release_cs())
    server.disconnect()
    return st.success("Critical Section Released")


def get_status():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 5052)
    server.connect()
    msg = server.get_status()
    st.write(str(msg))
    server.disconnect()
    return st.success("Status Refreshed")
    
if os.environ['temp_serverUp'] == 'false':
    os.environ['temp_serverUp'] = 'true'



def save_uploadedfile(fileContent,fileName,platformName,ipAddress):
    server = RPCContentServer(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    server.upload_file(fileContent,fileName,platformName,ipAddress)
    server.disconnect()
    return st.success("File registed with the server")

#st.write(get_serverList())

col1,col2,col3 = st.columns(3)

with col1:

    get_status()

with col2:
    platform = st.selectbox(
        'Please select the Subject for which you want to update the content',
        ('DC', 'CSIS', 'SF', 'DW'))
    uploaded_file = st.file_uploader("Choose a file")
    if st.button('Upload File'):
        req_status = request_criticalSection()
        if req_status == 'Granted':
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
        else:
            st.write('Access to Critical Section was not Granted')

with col3:
    
    init_register_contentServer() ## This would Register the CS Info with the Server

    if st.button('Initialize Content Server'):
        init_contentServer()
    
    ##if st.button('Request Critical Section'):
    ##    request_criticalSection()

    if st.button('Release Critical Section'):
        release_criticalSection()

    if st.button('Reset Environment Variables'):
       del os.environ['temp_serverUp']
   