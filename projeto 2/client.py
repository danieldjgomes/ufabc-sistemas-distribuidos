import socket
import json
import random
import threading
from message import Message



class Client:
    def __init__(self):
        self.servers = [('127.0.0.1', 10097), ('127.0.0.1', 10098), ('127.0.0.1', 10099)]
        self.map = {}
        
    def put(self, key, value):
        self.map[key] = value

    def get(self, key):
        if key in self.map.keys():
            return self.map[key]
        return None
        

    def sendRequest(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.server)
                sock.sendall(json.dumps(message.to_json()).encode())
                response = sock.recv(1024).decode()   
            return json.loads(response)
        except Exception as e:
            pass
            
    def requestInit(self):
        while True:
            userInput = input("Escreva 'INIT' para inicializar o cliente: ")
            if(userInput == "INIT"):
                break

    def process_put(self, targetServer, key, value):
        message = Message("PUT", key, (value, None))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(targetServer)
                sock.sendall(json.dumps(message.to_json()).encode())
                responseServer = sock.recv(1024).decode()   
        except Exception as e:
            pass

        response = Message.from_json(responseServer)
        if response.method == "PUT_OK":
            print(f"PUT_OK key: [{response.key}] value: [{(response.value)[0]}] timestamp: [{(response.value)[1]}] realizada no servidor [127.0.0.1:{(targetServer)[1]}]")
            self.put(key, response.value)

    def process_get(self, targetServer,key):
        localValue = self.get(key)
        localTimestamp = None if localValue == None else localValue[1]
        message = Message("GET", key, (None,(localTimestamp)))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(targetServer)
                sock.sendall(json.dumps(message.to_json()).encode())
                responseServer = sock.recv(1024).decode()   
        except Exception as e:
            pass       
        
        response = Message.from_json(responseServer)
        if response.method == "NULL":
            print("Chave não encontrada")
        elif response.method == "TRY_OTHER_SERVER_OR_LATER":
            print("Tente outro servidor ou mais tarde")
        else:
            self.put(key, response.value)
            print(f"GET key: [{response.key}] value: [{response.value[0]}] obtido do servidor [127.0.0.1:{(targetServer)[1]}], meu timestamp [[{str(response.value[1]) if localTimestamp == None else localTimestamp}]] e do servidor [{str(response.value[1])}]")

    def run(self):
        targetServer = random.choice(self.servers)
        print("Opções:")
        print("1. PUT")
        print("2. GET")
        choice = input("Escolha a ação: ")

        if choice == "1":
            key = input("Insira a chave: ")
            value = input("Insira o valor: ")
            threading.Thread(target=self.process_put, args=(targetServer, key , value)).start()
        elif choice == "2":
            key = input("Enter the key: ")
            threading.Thread(target=self.process_get, args=(targetServer,key)).start()
        else:
            print("Opção inválida")

    def callMethods(self):
        while True:
            self.run()
    
client = Client()
client.requestInit()
client.callMethods()
