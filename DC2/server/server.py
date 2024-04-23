from rpcServer import RPCServer

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



#print(ip.get())
#myPublicIp = ip.get()
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='a') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

logger.info("Server Started at IP address " + str(socket.gethostbyname(socket.gethostname())))
logger.info("Server Started at Port Number " + str(8080))

serverName = str(socket.gethostbyname(socket.gethostname())) + ':' + str(8080)
fileFound = 'No'
con = sqlite3.connect("metadata.db")
cur = con.cursor()
#cur.execute("DROP TABLE IF EXISTS files")
cur.execute("CREATE TABLE IF NOT EXISTS files(platform,filename, filehasvalue, filemd5value,uploadedon,ipaddress, filestatus)")
#cur.execute("DROP TABLE IF EXISTS servers")
cur.execute("CREATE TABLE IF NOT EXISTS servers(contentServerName, contentServerIP, contentServerPort)")
cur.close()
con.close()

if not os.path.isdir('../content'):
            os.mkdir('../content')
if not os.path.isdir('../content/DC'):
            os.mkdir('../content/DC')
if not os.path.isdir('../content/CSIS'):
            os.mkdir('../content/CSIS')
if not os.path.isdir('../content/SF'):
            os.mkdir('../content/SF')
if not os.path.isdir('../content/DW'):
            os.mkdir('../content/DW')

def func_hash_file(platformName,filename):
   logger.info("Inside Hash File Value Function")
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha1()
   fullFileName = '../content/' + str(platformName) + '/' + str(filename)
   # open file for reading in binary mode
   with open(fullFileName,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

def func_hash_filename(filename):
    logger.info("Inside Hash File Name")
    hash_file= hashlib.sha1(filename.encode('utf-8')).hexdigest()
    return hash_file


def register_metadata(platformName,filename,ipaddress):
    logger.info("Inside Register Metadata Function")
    md5 = func_hash_file(platformName,filename)
    filehashvalue = func_hash_filename(filename)
    currentTime = str(datetime.datetime.now())
    #logger.info(md5)
    #logger.info(filehashvalue)
    con = sqlite3.connect("metadata.db")
    cur = con.cursor()
    cur.execute("""
    INSERT INTO files VALUES
        ('""" + platformName + """','""" + filename + """','""" + filehashvalue + """','""" + md5 + """','""" + currentTime + """','""" + ipaddress + """','Active')
""")
    con.commit()
    logger.info("File Metadata Written to the Database")
    return 'File Registered Successully'

def clear_metadata():
    cur.execute("delete from files")

def upload_file(fileContent,fileName,platformName,ipAddress):
    logger.info("Inside Upload File Function")
    fullFileName = '../content/' + str(platformName) + '/' + str(fileName)
    with open(fullFileName,"w") as f:
         f.write(fileContent)
    f.close()
    logger.info("File Uploaded to the server")
    register_metadata(platformName,fileName,ipAddress)
    return 'Registed Successully'

def register_server(serverName,serverIP,serverPort):
    logger.info("Inside Register Function")
    logger.info(serverName)
    logger.info(serverIP)
    logger.info(serverPort)

    con_server = sqlite3.connect("metadata.db")
    cur_server = con_server.cursor()
    cur_server.execute("""
    INSERT INTO servers VALUES
        ('""" + str(serverName) + """','""" + str(serverIP) + """','""" + str(serverPort) + """') 
        """)
    con_server.commit()
    logger.info("Server Registered Successfully")
    return 'Server Registered Successully'

def get_serverList():
    con1 = sqlite3.connect("metadata.db")
    cur1 = con1.cursor()
    serverArr = np.empty((2,3))
    i = 0
    for row in cur1.execute("SELECT * FROM servers"):
        serverArr[i][0] = row['contentServerName']
        serverArr[i][1] = row['contentServerIP']
        serverArr[i][2] = row['contentServerPort']
    print(serverArr)
    return serverArr

server = RPCServer()

server.registerMethod(register_metadata)
server.registerMethod(upload_file)
server.registerMethod(register_server)
server.registerMethod(get_serverList)

server.run()
