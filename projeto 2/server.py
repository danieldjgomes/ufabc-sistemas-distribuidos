import socket
import json
import threading
from message import Message



class Server:
    
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = None
        self.leaderIp = self.ip 
        self.leaderPort = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.leaderSocket = None
        self.validServerPorts = [10097, 10098, 10099]
        self.isLeader = None

    def setPortSettings(self):
        leaderPort = None
        activePorts = []
        for port in self.validServerPorts:
             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.connect((self.ip, port))
                    print("Calling server" + str(port))
                    sock.sendall(json.dumps(Message("isLeader", None).to_json()).encode())  
                    isLeader = sock.recv(1024).decode()
                    if(json.loads(isLeader).get("value") == True):
                        leaderPort = port
                    else:
                        activePorts.append(port)
                except Exception as e:
                    print(e)  
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
        print(f"Server is listening on {self.ip}:{self.port}")
        while True:
            conn, addr = self.socket.accept()
            print(f"New connection from {addr}")
            threading.Thread(target=self.handleClients, args=(conn, addr)).start()
        
    def handleClients(self, conn, addr):
        data = conn.recv(1024).decode()
        print(data)
        message = Message.from_json(json.loads(data))

        print(f"Handling {addr}")

        if message.method == "isLeader":
            response = self.isLeader
            response_message = Message("isLeaderResponse", response)
            conn.sendall(json.dumps(response_message.to_json()).encode())
        conn.close()

Server().start()
