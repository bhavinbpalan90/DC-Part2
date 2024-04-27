from rpcServer import RPCServer
from rpcClient import RPCClient
import xmlrpc
#import xmlrpclib
from xmlrpc.server import SimpleXMLRPCServer
import sys
import os.path
import logging
import socket
#import public_ip as ip
import sqlite3
import datetime
import hashlib
from hashlib import sha512
import base64
import numpy as np
import pandas as pd
import json



#print(ip.get())
#myPublicIp = ip.get()
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 
serverlist = pd.DataFrame()
logger.info("Content Server 1 Started at IP address " + str(socket.gethostbyname(socket.gethostname())))
logger.info("Server Started at Port Number " + str(5052))

cp_serverName = '3'
cp_serverIP = str(socket.gethostbyname(socket.gethostname()))
cp_serverPort = 5052
cp_holdToken = False
cp_in_critical_section = False
#global token_array
#token_array = [0]
#global token_queue
#token_queue = []


#serverName = str(socket.gethostbyname(socket.gethostname())) + ':' + str(5050)

def register_server():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    server.register_server(cp_serverName,cp_serverIP,cp_serverPort)
    server.disconnect()
    print("Content Provider Info registed with the server")
    logger.info('CP Info registed with the server')
    return "Completed"


def get_serverList():
    server = RPCClient(str(socket.gethostbyname(socket.gethostname())), 8080)
    server.connect()
    serv_list = server.get_serverList()
    logger.info('Server List is as below:')
    logger.info(serv_list)
    print(serv_list)
    server.disconnect()
    return serv_list

def initialize_requestArray():
    print("Initialization of Request Array Started on Content Server...")
    logger.info("Initialization of Request Array Started on Content Server...")
    global initial_seq 
    initial_seq = 0
    serv_list = (get_serverList())
    y = json.loads(serv_list)
    global df_serverList
    df_serverList = pd.DataFrame(y)
    df_serverList = df_serverList.rename(columns={'0': 'ServerName', '1': 'ServerIP', '2': 'ServerPort'})
    print(df_serverList)
    no_of_sites = len(df_serverList.index)
    global request_array
    request_array = [0] * no_of_sites
    print(request_array)
    logger.info(request_array)
    if cp_holdToken == True:
        initialize_tokens()
    return 'Initialized Request Array'

def initialize_tokens():
    print("Initialization of Token Started on Content Server...")
    logger.info("Initialization of Token Started on Content Server...")
    global initial_seq 
    initial_seq = 0
    serv_list = (get_serverList())
    y = json.loads(serv_list)
    df_serverList = pd.DataFrame(y)
    df_serverList = df_serverList.rename(columns={'0': 'ServerName', '1': 'ServerIP', '2': 'ServerPort'})
    print(df_serverList)
    no_of_sites = len(df_serverList.index)
    global token_array
    token_array = [0] * no_of_sites
    global token_queue
    token_queue = []
    #token_queue.append('a')
    print(token_array)
    logger.info(token_array)
    #print(token_queue[0])
    #token_queue.pop(0)
    print(token_queue)
    logger.info(token_queue)
    os.environ['temp_cs_access_granted'] = 'true'
    return 'Initialized Token Array'

def bdcst_requestArray_change(position,value):
    for index, row in df_serverList.iterrows():
        serverIP = row['ServerIP']
        serverPort = int(row['ServerPort'])
        server = RPCClient(serverIP, serverPort)
        server.connect()
        print(server.update_requestArray(position,value))
        server.disconnect()
    return 'Broadcast Completed'



def update_requestArray(position,value):
    curr_value = int(request_array[position])
    if int(value) > curr_value: ## To check the Outdated Request
        request_array[position] = int(value)
        if cp_holdToken == True:
            update_token(position,value)
    print(request_array)
    return 'Request Array Updated'


def update_token(position,value):
    print('Inside Token Update')
    if len(token_queue) > 0:
        if str(int(position)+1) not in token_queue:
            token_queue.append(int(position)+1) ## Update the queue with site requesting for token
    else:
        token_queue.append(str(int(position)+1))
    print('Token Queue below:')
    print(token_queue)
    curr_value = int(token_array[position])
    if int(value) == curr_value + 1: ## To check the Outstanding Request
        print('Grant Token')
    print('Token Array Below')
    print(token_array)
    return 'Token Updated'



def send_token(serverIP,serverPort,tokenArray,tokenQueue):
    server = RPCClient(serverIP, int(serverPort))
    server.connect()
    print(server.recieve_token(tokenArray,tokenQueue))
    server.disconnect()
    global cp_holdToken
    cp_holdToken = False
    return 'Token is Sent'

def recieve_token(tokenArray,tokenQueue):
    global token_array
    token_array = tokenArray
    print(token_array)
    global token_queue
    token_queue = tokenQueue
    print(token_queue)
    global cp_holdToken
    cp_holdToken = True
    return 'Token Recieved'
    

def request_cs():
    position = int(cp_serverName) - 1
    request_array[position] =  request_array[position] + 1
    logger.info(request_array)
    print(request_array)
    if cp_holdToken == True:
        print('Site already holding a token')
        bdcst_requestArray_change(position,int(request_array[position]))
        global cp_in_critical_section
        cp_in_critical_section = True
        return 'Granted'
    else:
        print('Broadcasting to request for Token')
        bdcst_requestArray_change(position,int(request_array[position]))
        #print('Response of Broadcast: ' + status)
        return 'Access to Critical section not available now. Please try after some time..'
    logger.info('Broadcasted to Other Sites')
    return 'Wait'

def release_cs():
    position = int(cp_serverName) - 1
    token_array[position] = request_array[position]
    if len(token_queue) > 0:
        next_site = token_queue[0]
        print('Next Site: ' + str(next_site))
        if str(next_site) != "":
            df_next_site_address = df_serverList.loc[df_serverList['ServerName'] == str(next_site)]
            print(df_next_site_address)
            token_queue.pop(0)
            send_token(str(df_next_site_address['ServerIP'].iloc[0]),int(df_next_site_address['ServerPort'].iloc[0]),token_array,token_queue)
            global cp_holdToken
            cp_holdToken = False
            global cp_in_critical_section
            cp_in_critical_section = False
            
    else:
        print('No Site in the Token Queue')
    return 'Release Completed'

def get_status():
    final_msg = 'Status for Server ' + str(cp_serverName) + ' || ';
    try:    
        final_msg += 'Site Token Status: ' + str(cp_holdToken) + ' || '
    except:
        final_msg += 'Site Token Yet to be Initialized || ' 
    
    try:    
        final_msg += 'Site Executing CS: ' + str(cp_in_critical_section) + ' || '
    except:
        final_msg += 'Site Not Executing CS || ' 

    try:    
        final_msg += 'Request Array : ' + str(request_array) + ' || '
    except:
        final_msg += 'Request Array yet to be initialized || ' 
    
    try:
        if cp_holdToken == True:
            final_msg += 'Token Array : ' + str(token_array) + ' || '
        else:
            final_msg += 'Token Array yet to be initialized || ' 
    except:
        final_msg += 'Token Array yet to be initialized || ' 
   
    try:    
        if cp_holdToken == True:
            final_msg += 'Token Queue : ' + str(token_array) + ' || '
        else:
            final_msg += 'Token Queue yet to be initialized' 
    except:
        final_msg += 'Token Queue yet to be initialized ' 
   
    return final_msg




server = RPCServer()

server.registerMethod(register_server)
server.registerMethod(get_serverList)
server.registerMethod(initialize_requestArray)
server.registerMethod(initialize_tokens)
server.registerMethod(request_cs)
server.registerMethod(update_requestArray)
server.registerMethod(bdcst_requestArray_change)
server.registerMethod(release_cs)
server.registerMethod(send_token)
server.registerMethod(recieve_token)
server.registerMethod(get_status)

server.run()
