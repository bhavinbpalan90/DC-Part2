import sqlite3
import datetime
import hashlib
from hashlib import sha512
import base64
import streamlit as st
import sys
import os.path

st.set_page_config(layout="wide")

con = sqlite3.connect("metadata.db")
cur = con.cursor()
#cur.execute("DROP TABLE IF EXISTS files")
#cur.execute("CREATE TABLE IF NOT EXISTS files(platform,filename, filehasvalue, filemd5value,uploadedon,ipaddress, filestatus)")


def showfiles():
    for row in cur.execute("SELECT * FROM files"):
        st.write(row)

def showServers():
    for row in cur.execute("SELECT * FROM servers"):
        st.write(row)

col1,col2,col3 = st.columns(3)
with col1:
    showServers()
with col2:
    logfile = str(os.getcwd()) + "\std.log"
    f = open(logfile, "r")
    lines = f.readlines()
    for line in lines:
        st.write(line)

with col3:
    showfiles()
#clear_metadata()
#register_metadata('movie1.txt','12.12.12.12')