import socket
import json
import random
import time
from message import Message


class Client:
    def __init__(self):
        self.servers = [('127.0.0.1', 10097), ('127.0.0.1', 10098), ('127.0.0.1', 10099)]
        self.server = None

    def chooseServer(self):
        self.server = random.choice(self.servers)

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
            

    def run(self):
        while True:
            self.chooseServer()
            print("Opçoes:")
            print("1. PUT")
            print("2. GET")
            choice = input("Escolha a ação: ")

            if choice == "1":
                key = input("Insira a chave: ")
                value = input("Insira o valor: ")
                response = self.sendRequest(Message("PUT", key, (value, None)))
                response = Message.from_json(response)
                if (response.method == "PUT_OK"):
                    print(f"PUT_OK key: [{key}] value: [{value}] timestamp: [{str(int(time.time()))}] realizada no servidor [127.0.0.1:{(self.server)[1]}]")

            elif choice == "2":
                key = input("Enter the key: ")
                response = self.sendRequest(Message("GET", key, int(time.time())))
                response = Message.from_json(response)
                if response.method == "NULL":
                    print("Chave não encontrada")
                elif response.method == "TRY_OTHER_SERVER_OR_LATER":
                    print("Tente outro servidor ou mais tarde")
                else:
                    print(f"GET key: [{response.key}] value: [{response.value[0]}] obtido do servidor [127.0.0.1:{(self.server)[1]}], meu timestamp [{str(int(time.time()))}] e do servidor [{str(response.value[1])}]")


            else:
                print("Opção inválida")


client = Client()
client.requestInit()
client.run()
