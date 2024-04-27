import json
import socket
import inspect
from threading import Thread
import logging

logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

SIZE = 1024
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)
## printing the hostname and ip_address
logger.info(f"Hostname: {hostname}")
logger.info(f"IP Address: {ip_address}")




class RPCServer:

    def __init__(self, host:str=ip_address, port:int=5052) -> None:
        self.host = host
        self.port = port
        self.address = (host, port)
        self._methods = {}

    def help(self) -> None:
        logger.info('REGISTERED METHODS:')
        for method in self._methods.items():
            logger.info('\t',method)

    '''

        registerFunction: pass a method to register all its methods and attributes so they can be used by the client via rpcs
            Arguments:
            instance -> a class object
    '''
    def registerMethod(self, function) -> None:
        try:
            self._methods.update({function.__name__ : function})
        except:
            raise Exception('A non method object has been passed into RPCServer.registerMethod(self, function)')

    '''
        registerInstance: pass a instance of a class to register all its methods and attributes so they can be used by the client via rpcs
            Arguments:
            instance -> a class object
    '''
    def registerInstance(self, instance=None) -> None:
        try:
            # Regestring the instance's methods
            for functionName, function in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not functionName.startswith('__'):
                    self._methods.update({functionName: function})
        except:
            raise Exception('A non class object has been passed into RPCServer.registerInstance(self, instance)')

    '''
        handle: pass client connection and it's address to perform requests between client and server (recorded fucntions or) 
        Arguments:
        client -> 
    '''
    def __handle__(self, client:socket.socket, address:tuple):
        logger.info(f'Managing requests from {address}.')
        while True:
            try:
                functionName, args, kwargs = json.loads(client.recv(SIZE).decode())
            except: 
                logger.info(f'! Client {address} disconnected.')
                break
            # Showing request Type
            logger.info(f'> {address} : {functionName}({args})')
            
            try:
                response = self._methods[functionName](*args, **kwargs)
            except Exception as e:
                # Send back exeption if function called by client is not registred 
                client.sendall(json.dumps(str(e)).encode())
            else:
                client.sendall(json.dumps(response).encode())


        logger.info(f'Completed request from {address}.')
        client.close()
    
    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.address)
            sock.listen()

            logger.info(f'+ Server {self.address} running')
            while True:
                try:
                    client, address = sock.accept()

                    Thread(target=self.__handle__, args=[client, address]).start()

                except KeyboardInterrupt:
                    logger.info(f'- Server {self.address} interrupted')
                    break
