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
        self.map[key] = value
        print(self.map)

    def get(self, key):
        if key in self.map.keys():
            return self.map[key]
        return None

    def setPortSettings(self):
        leaderPort = None
        activePorts = []
        for port in self.validServerPorts:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.settimeout(1)
                    sock.connect((self.ip, port))
                    print("Calling server " + str(port))
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
        while True:
            try:
                inputPort = int(input("Enter ServerLeader the port number: "))
                if inputPort in self.validServerPorts:
                    if leaderPort == None:  
                        if inputPort == self.port:
                            print("The server is the leader.")
                            self.isLeader = True
                            break
                    else:
                        if inputPort == leaderPort:
                            self.isLeader = False
                            self.leaderPort = inputPort
                            break
                else:
                    print("Invalid port. Please enter a valid port number: 10097, 10098, or 10099")
            except ValueError:
                pass
        

    def setPort(self, activePorts):
        while True:
            try:
                inputPort = int(input("Enter server the port number: "))
                if inputPort in self.validServerPorts:
                    if not (inputPort in activePorts):
                        self.port = inputPort
                        break
                else:
                    print("Invalid port. Please enter a valid port number: 10097, 10098, or 10099")
            except ValueError:
                pass

    def start(self):
        # Get server port and leader info
        self.setPortSettings()

        self.socket.bind((self.ip, self.port))
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            threading.Thread(target=self.handleClients, args=(conn, addr)).start()
        
    def handleClients(self, conn, addr):
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
        self.put(message.key, message.value)
        conn.sendall(json.dumps(Message("REPLICATION_OK", None, None).to_json()).encode())

    def doGet(self, conn, message):
        timestamp = int(time.time())
        item = self.get(message.key)
        if item == None:
            conn.sendall(json.dumps(Message("NULL", item, None).to_json()).encode())
        else:
            if item[1] > timestamp:
                conn.sendall(json.dumps(Message("TRY_OTHER_SERVER_OR_LATER", None, None).to_json()).encode())
            else:
                conn.sendall(json.dumps(Message("GET_OK", message.key, item).to_json()).encode())

    def doPut(self, conn, message):
        if(self.isLeader):
            self.doLeaderPut(conn, message)
        else:
            self.doServerPut(conn, message)

    def doServerPut(self, conn, message):
        print("Server put to leader ", self.leaderPort)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    try:
                        sock.connect((self.ip, self.leaderPort))
                        sock.sendall(json.dumps(message.to_json()).encode())  
                        replication = sock.recv(1024).decode()
                        putOk = sock.recv(1024).decode()  
                    except Exception as e:
                        print(e)
        conn.sendall(json.dumps(Message("PUT_OK", None, None).to_json()).encode())

    def doLeaderPut(self, conn, message):
        timestamp = int(time.time())
        self.put(message.key,(message.value, timestamp))
        message.method = "REPLICATION"
        message.value = (message.value[0], timestamp)
        for port in self.validServerPorts:
            if port != self.leaderPort:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    try:
                        sock.settimeout(1)
                        sock.connect((self.ip, port))
                        sock.sendall(json.dumps(message.to_json()).encode())  
                        serveResponse = sock.recv(1024).decode()
                        print("Leader sent to server" + str(port))      
                    except Exception as e:
                        print(e)
        conn.sendall(json.dumps(Message("PUT_OK", None, None).to_json()).encode())

Server().start()
