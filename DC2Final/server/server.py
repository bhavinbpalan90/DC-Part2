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
import pandas as pd
import json



#print(ip.get())
#myPublicIp = ip.get()
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='a') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 
serverlist = pd.DataFrame()
logger.info("Server Started at IP address " + str(socket.gethostbyname(socket.gethostname())))
logger.info("Server Started at Port Number " + str(8080))

serverName = str(socket.gethostbyname(socket.gethostname())) + ':' + str(8080)
fileFound = 'No'
con = sqlite3.connect("metadata.db")
cur = con.cursor()
#cur.execute("DROP TABLE IF EXISTS files")
cur.execute("CREATE TABLE IF NOT EXISTS files(platform,filename, filehasvalue, filemd5value,uploadedon,ipaddress, filestatus)")
cur.execute("DROP TABLE IF EXISTS servers")
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

def deactivate_duplicateFile(platformName,filename):
    logger.info("Inside Deactivate Duplicate Files Function")
    calc_filehashvalue = func_hash_filename(filename)
    #logger.info(md5)
    #logger.info(filehashvalue)
    con = sqlite3.connect("metadata.db")
    cur = con.cursor()
    logger.info("""
UPDATE files set filestatus = 'Inactive' where platform = '""" + platformName + """' and filehasvalue = '""" + calc_filehashvalue + """'
""")
    cur.execute("""
    UPDATE files set filestatus = 'Inactive' where platform = '""" + platformName + """' and filehasvalue = '""" + calc_filehashvalue + """'
""")
    con.commit()
    logger.info("Duplicate file was changed to inactive")
    return 'File Registered Successully'       

def register_metadata(platformName,filename,ipaddress):
    logger.info("Inside Register Metadata Function")
    md5 = func_hash_file(platformName,filename)
    filehashvalue = func_hash_filename(filename)
    currentTime = str(datetime.datetime.now())
    #logger.info(md5)
    #logger.info(filehashvalue)
    con = sqlite3.connect("metadata.db")
    cur = con.cursor()
    logger.info("""
    INSERT INTO files VALUES
        ('""" + platformName + """','""" + filename + """','""" + filehashvalue + """','""" + md5 + """','""" + currentTime + """','""" + ipaddress + """','Active')
""")
    cur.execute("""
    INSERT INTO files VALUES
        ('""" + platformName + """','""" + filename + """','""" + filehashvalue + """','""" + md5 + """','""" + currentTime + """','""" + ipaddress + """','Active')
""")
    con.commit()
    logger.info("File Metadata Written to the Database")
    return 'Success'

def clear_metadata():
    cur.execute("delete from files")

def upload_file(fileContent,fileName,platformName,ipAddress):
    logger.info("Inside Upload File Function")
    deactivate_duplicateFile(platformName,fileName)
    reg_Status = register_metadata(platformName,fileName,ipAddress)
    if reg_Status == 'Success':
        fullFileName = '../content/' + str(platformName) + '/' + str(fileName)
        with open(fullFileName,"w") as f:
              f.write(fileContent)
        f.close()
    logger.info("File Uploaded to the server")
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
    logger.info("Inside Get Server List Function")
    con1 = sqlite3.connect("metadata.db")
    
    cur1 = con1.cursor()
    cur1.execute("SELECT DISTINCT * FROM servers")
    serverlist = pd.DataFrame(cur1.fetchall())
    json_str = serverlist.to_json(orient='records')
    print(json_str)
    logger.info(json_str)
    return json_str

def checkFileexistLocal(Platform, FileName):
    logger.info("Checking for " + Platform + " \ " + FileName + " on Local Server" )
    con2 = sqlite3.connect('metadata.db')
    cur2 = con2.cursor()
    cur2.execute("""
                 SELECT * FROM files where filestatus = 'Active' and platform = '""" + Platform + """' and filename = '""" + FileName + """'
                 """)
    filelist = pd.DataFrame(cur2.fetchall())
    if len(filelist) > 0:
          return 'Found'
    else:
          return 'NotFound'

def movefile(Platform, FileName,OriginServer):
    logger.info("Inside Move file Function")
    logger.info(str(OriginServer))
    fileFound = checkFileexistLocal(Platform, FileName)
    logger.info('Status of file check local: ' + str(fileFound))
    filepath = '../content/' + str(Platform) + '/' + str(FileName)
    if fileFound != 'NotFound':
        try:
            with open(filepath,"r") as handle:
                resultOutput = str(handle.read())
                logger.info('File Founded Locally and is sent')
                #logger.info(resultOutput)
                handle.close()
                return str(resultOutput)
        except:
            return 'File Not Found'
    else:
          return 'File Not Found'    
    

server = RPCServer()

server.registerMethod(register_metadata)
server.registerMethod(upload_file)
server.registerMethod(register_server)
server.registerMethod(get_serverList)
server.registerMethod(movefile)

server.run()
