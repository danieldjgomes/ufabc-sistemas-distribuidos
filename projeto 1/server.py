import socket
import json
import threading
import os

class P2PServer:
    ## Monta as variaveis globais do projeto
    def __init__(self):
        self.listOfPeers = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 12346

    ## Inicia a execução
    def start(self):
        self.s.bind(('', self.port))
        self.s.listen(1)
        while True:
            c, addr = self.s.accept()
            threading.Thread(target=self.run, args=(c, addr)).start()

    def run(self, c, addr):
        
        
        def doUpdate(c, addr, data):
            ## Recebe, executa o UPDATE e returna a resposta ao peer
            if 'data' in data and 'files' in data['data']:
                files = data['data']['files']
                self.listOfPeers[addr[1]] = files
                c.sendall(b'UPDATE_OK')
            else:
                print("Json Inválido")

        def doSearch(c, addr, data):
            ## Busca o arquivo na lista de peers pelo nome e reporta os peers que correspondem a pesquisa
            search = data['data']['query']
            result = []
            print(search)
            print("Peer {}:{} solicitou arquivo {}".format(addr[0], addr[1], search))
            for key, values in self.listOfPeers.items():
                if search in values:
                    result.append(key)
            c.sendall(str(result).encode())

        def doJoin(c, addr, data):
            ## Executa a lógica de JOIN
            files = data['data']['filesPath']
            self.listOfPeers[addr[1]] = os.listdir(files)
            print("Peer {}:{} adicionado com os arquivos {}".format(addr[0], addr[1], os.listdir(files)))
            c.send(b'JOIN_OK')

        def receiveData(c):
            ## Lê a chamada dos peers e decodifica
            data = ""
            while True:
                try:
                    received = c.recv(1024)
                    data += received.decode()
                except:
                    return data
                else:
                    return data

        c.settimeout(2)
      
        while True:
            call = receiveData(c)

            try:
                ## Executa as ações de acordo com a chamada dos peers
                if call != "":
                    data = json.loads(call)

                    if data['method'] == "JOIN":
                        threading.Thread(target=doJoin, args=(c, addr, data)).start()

                    if data['method'] == "SEARCH":
                        threading.Thread(target=doSearch, args=(c, addr, data)).start()
                    
                    if data['method'] == "UPDATE":
                        threading.Thread(target=doUpdate, args=(c, addr, data)).start()                

            except json.JSONDecodeError as e:
                print("Error decoding JSON data:", str(e))


## Cria objeto e executa
server = P2PServer()
server.start()
