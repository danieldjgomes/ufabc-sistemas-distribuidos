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
        """
        Armazena um par chave-valor no mapa local.

        Args:
            key (str): Chave a ser armazenada.
            value (str): Valor correspondente à chave.

        """
        self.map[key] = value

    def get(self, key):
        """
        Retorna o valor associado a uma chave.

        Args:
            key (str): Chave a ser pesquisada.

        Returns:
            str: Valor associado à chave, ou None se a chave não existir.

        """
        if key in self.map.keys():
            return self.map[key]
        return None

    def sendRequest(self, message):
        """
        Envia uma solicitação para um servidor e retorna a resposta.

        Args:
            message (Message): Objeto Message contendo a solicitação.

        Returns:
            dict: Dicionário contendo a resposta do servidor.

        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(self.server)
                sock.sendall(json.dumps(message.to_json()).encode())
                response = sock.recv(1024).decode()
            return json.loads(response)
        except Exception as e:
            pass

    def requestInit(self):
        """
        Solicita ao usuário que digite 'INIT' para inicializar o cliente.

        """
        while True:
            userInput = input("Escreva 'INIT' para inicializar o cliente: ")
            if(userInput == "INIT"):
                break

    def doPut(self, targetServer, key, value):
        """
        Executa a operação PUT no servidor alvo.

        Args:
            targetServer (tuple): Tupla contendo o endereço IP e a porta do servidor.
            key (str): Chave a ser armazenada.
            value (str): Valor correspondente à chave.

        """
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

    def doGet(self, targetServer,key):
        """
        Executa a operação GET no servidor alvo.

        Args:
            targetServer (tuple): Tupla contendo o endereço IP e a porta do servidor.
            key (str): Chave a ser pesquisada.

        """
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
        """
        Executa o cliente, oferecendo opções para realizar operações PUT ou GET.

        """
        targetServer = random.choice(self.servers)
        print("Opções:")
        print("1. PUT")
        print("2. GET")
        choice = input("Escolha a ação: ")

        if choice == "1":
            key = input("Insira a chave: ")
            value = input("Insira o valor: ")
            threading.Thread(target=self.doPut, args=(targetServer, key , value)).start()
        elif choice == "2":
            key = input("Insira a chave: ")
            threading.Thread(target=self.doGet, args=(targetServer,key)).start()
        else:
            print("Opção inválida")

    def callMethods(self):
        """
        Executa continuamente o método run().

        """
        while True:
            self.run()

client = Client()
client.requestInit()
client.callMethods()
