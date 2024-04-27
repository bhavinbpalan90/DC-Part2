from rpcClient import RPCClient
import os.path
import streamlit as st
import pathlib
import socket



st.set_page_config(layout="wide")

col1, col2,col3 = st.columns([1,4,2])
with col1:
    input_ipaddress = st.text_input('Server IP Address',str(socket.gethostbyname(socket.gethostname())))
    input_port = st.text_input('Port No',8080)

with col2:
    input_platform = st.selectbox(
        'Please select the Subject from which you want the content ?',
        ('DC', 'CSIS', 'SF', 'DW'))

    input_fileName = st.text_input('File Name', '')

    if st.button('Get File') and input_fileName != '':
        server = RPCClient(str(input_ipaddress), int(input_port))
        server.connect()
        try:

            Platform=str(input_platform)

            fileName = str(input_fileName)

            content = str(server.movefile(str(Platform),str(fileName),str(input_ipaddress)))

            if content != 'File Not Found':

                if not os.path.isdir('Contents'):

                    os.mkdir('Contents')

                directory = 'Contents/' + str(Platform) + '/'

                if not os.path.isdir(directory):

                    os.mkdir(directory)

                    #st.write('directory created')

                ##file_path  = os.path.join(directory, fileName)

                file_path = str(os.getcwd()) + str('/Contents/') + str(Platform) + str('/') + str(fileName)

                #st.write(file_path)

                handle=open(file_path,"w")

                #content = str(server.movefile(str(Platform),str(fileName),str(input_ipaddress)))

                handle.write(content)

                st.write('File Downloaded and available at ' + str(file_path))

                handle.close()

            else:

                st.write('File Not Available')

        except:
            st.write ('Download failed')
        server.disconnect()

with col3:
    st.write('All files available locally are as below: ')
    Content = pathlib.Path('Contents/')
    for files in Content.rglob('*.*'):
        st.write(files)
