import socket
import json
import threading
from message import Message
import time

class Server:
    
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = None
        self.leaderIp = self.ip 
        self.leaderPort = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.validServerPorts = [10097, 10098, 10099]
        self.isLeader = None
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

    def setPortSettings(self):
        """
        Configura as portas ativas e a porta do líder.

        """
        leaderPort = None
        activePorts = []
        for port in self.validServerPorts:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.settimeout(1)
                    sock.connect((self.ip, port))
                    sock.sendall(json.dumps(Message("isLeader", None,None).to_json()).encode())  
                    isLeader = sock.recv(1024).decode()
                    message = Message.from_json(json.loads(isLeader))
                    if(message.value == True):
                        leaderPort = port
                        activePorts.append(port)
                    else:
                        activePorts.append(port)
                except Exception:
                    pass
        self.setPort(activePorts)
        self.setLeaderPort(leaderPort)

    def setLeaderPort(self, leaderPort):
        """
        Define a porta do líder.

        Args:
            leaderPort (int): Porta do líder.

        """
        while True:
            try:
                inputPort = int(input("Insira a porta do server líder: "))
                if inputPort in self.validServerPorts:
                    if leaderPort == None:  
                        if inputPort == self.port:
                            self.isLeader = True
                            self.leaderPort = inputPort
                            break
                    else:
                        if inputPort == leaderPort:
                            self.isLeader = False
                            self.leaderPort = inputPort
                            break
                else:
                    print("Entrada inválida, as portas devem pertencer ao grupo [10097, 10098, 10099].")
            except ValueError:
                pass
        

    def setPort(self, activePorts):
        """
        Define a porta do servidor.

        Args:
            activePorts (list): Lista de portas ativas.

        """
        while True:
            try:
                inputPort = int(input("Insira o número da porta do servidor: "))
                if inputPort in self.validServerPorts:
                    if not (inputPort in activePorts):
                        self.port = inputPort
                        break
            except ValueError:
                pass

    def start(self):
        """
        Inicia o servidor.

        """
        self.setPortSettings()

        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            threading.Thread(target=self.handleClients, args=(conn, addr)).start()
        
    def handleClients(self, conn, addr):
        """
        Lida com as solicitações dos clientes.

        Args:
            conn (socket): Objeto socket da conexão.
            addr (tuple): Tupla contendo o endereço IP e a porta do cliente.

        """
        data = conn.recv(1024).decode()
        message = Message.from_json(data)

        if message.method == "isLeader":
            response = self.isLeader
            response_message = Message("isLeaderResponse", None, response)
            conn.sendall(json.dumps(response_message.to_json()).encode())
            
        elif message.method == "PUT":
            self.doPut(conn, message)
        elif message.method == "GET":
            self.doGet(conn, message)
        elif message.method == "REPLICATION":
            self.doReplication(conn, message)
        conn.close()
        

    def doReplication(self, conn, message):
        """
        Executa a replicação dos dados nos servidores.

        Args:
            conn (socket): Objeto socket da conexão.
            message (Message): Objeto Message contendo a solicitação de replicação.

        """
        self.put(message.key, message.value)
        conn.sendall(json.dumps(Message("REPLICATION_OK", None, None).to_json()).encode())

    def doGet(self, conn, message):
        """
        Executa a operação GET.

        Args:
            conn (socket): Objeto socket da conexão.
            message (Message): Objeto Message contendo a solicitação de GET.

        """
        item = self.get(message.key)
        if item is None:
            response = Message("NULL", None, None)
        elif message.value[1] is not None and item[1] < message.value[1]:
            response = Message("TRY_OTHER_SERVER_OR_LATER", None, None)
        else:
            response = Message("GET_OK", message.key, item)

        conn.sendall(json.dumps(response.to_json()).encode())


    def doPut(self, conn, message):
        """
        Executa a operação PUT.

        Args:
            conn (socket): Objeto socket da conexão.
            message (Message): Objeto Message contendo a solicitação de PUT.

        """
        if(self.isLeader):
            self.doLeaderPut(conn, message)
        else:
            self.doServerPut(conn, message)

    def doServerPut(self, conn, message):
        """
        Executa a operação PUT em um servidor não líder.

        Args:
            conn (socket): Objeto socket da conexão.
            message (Message): Objeto Message contendo a solicitação de PUT.

        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.ip, self.leaderPort))
                sock.sendall(json.dumps(message.to_json()).encode())  
                replication = sock.recv(1024).decode()
                putOk = sock.recv(1024).decode()  
                message = Message.from_json(putOk)
            except Exception as e:
                pass
        conn.sendall(json.dumps(Message("PUT_OK", message.key, message.value).to_json()).encode())

    def doLeaderPut(self, conn, message):
        """
        Executa a operação PUT no servidor líder.

        Args:
            conn (socket): Objeto socket da conexão.
            message (Message): Objeto Message contendo a solicitação de PUT.

        """
        timestamp = int(time.time())
        message.value = ((message.value)[0], timestamp)
        self.put(message.key,message.value)
        message.method = "REPLICATION"
        message.value = (message.value[0], timestamp)
        for port in self.validServerPorts:
            if port != self.leaderPort:
                print("Aguardando para replicar para o server " + str(port))
                time.sleep(10)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    try:
                        sock.settimeout(1)
                        sock.connect((self.ip, port))
                        sock.sendall(json.dumps(message.to_json()).encode())  
                        serveResponse = sock.recv(1024).decode()  
                    except Exception as e:
                        pass
        conn.sendall(json.dumps(Message("PUT_OK", message.key, ((message.value)[0], timestamp)).to_json()).encode())

Server().start()
