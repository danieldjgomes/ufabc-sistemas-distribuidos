import socket
import os
import threading
import json


class P2PClient:
    def __init__(self):
        self.isDownloading = False
        self.filesList = []
        self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverPort = 12346
        self.addressServer = '127.0.0.1'
        self.socketServer.connect((self.addressServer, self.serverPort))
        self.clientPort = self.socketServer.getsockname()[1]
        self.folderPeer = os.path.join(os.getcwd(), "p2p")
        if not os.path.isdir(self.folderPeer):
            os.mkdir(self.folderPeer)
        self.folderPeer = os.path.join(self.folderPeer, str(self.clientPort))
        os.mkdir(self.folderPeer)

    def setupClient(self):
        print("""
 ::::::::    :::        ::::::::::: :::::::::: ::::     ::: :::::::::::  ::::::::::
++:    +:+   :+:            :+:     :+:        :+:+:    :+:     :+:     :+:
+            +:+            +:+     +:+        +:+ +:+  +:+     +:+     +:+
+            +#+            +#+     +#++:++#   +#+  +#+ +#+     +#+     +#++:++
+            +#+            +#+     +#+        +#+   +#+#+#     +#+     +#+
+#      +++  #+#            #+#     #+#        #+#    #+#+#     #+#     #+#
 #########    ########## ########## ########## ###     ####     ###     ##########

        """)

        print("Está conectando no servidor: " + str(self.addressServer) + ":" + str(self.serverPort))
        while True:
            try:
                print("Digite 'JOIN' para iniciar.")
                entrada = input()
                if entrada == "JOIN":
                    break
            except Exception as e:
                print(f"Erro ao ler a entrada: {str(e)}")
        self.callJoin()

    def callJoin(self):
        pastaPeer = os.getcwd() + "/p2p/" + str(self.socketServer.getsockname()[1])
        pathArquivos = pastaPeer
        message = json.dumps({"method": "JOIN", "data": {"filesPath": pathArquivos}})
        self.socketServer.sendall(message.encode())

        if self.socketServer.recv(1024).decode() == "JOIN_OK":
            arquivos = os.listdir(pastaPeer)
            arquivosFormatados = ['"{}"'.format(item) for item in arquivos]
            arquivosConcatenados = ','.join(arquivosFormatados)
            print(f"Sou o Peer {self.addressServer}:{self.clientPort} com arquivos: {arquivosConcatenados}")
        else:
            raise Exception("Falha na Conexao! Programa finalizado.")

    def callUpload(self, socket):
        try:
            request = socket.recv(1024).decode()
            data = json.loads(request)
            filename = data["data"]["filename"]
            peer = data["data"]["port"]

            folder = os.path.join(os.path.join(os.getcwd(), "p2p"), str(peer))
            if filename in os.listdir(folder):
                path = os.path.join(folder, filename)
                size = os.path.getsize(path)
                response = {"status": "OK", "fileSize": size}
                socket.send(json.dumps(response).encode())
                self.isDownloading = True
                while True:
                    userInput = input("Gostaria de Aprovar o download? (SIM/NAO): ")
                    if userInput == "SIM":
                        response = {"status": "downloadAccepted"}
                        socket.send(json.dumps(response).encode())
                        size = os.path.getsize(path)
                        bytes = 0
                        sendRate = 1024 * 1024 * 1024
                        with open(path, "rb") as file:
                            while True:
                                data = file.read(sendRate)
                                if not data:
                                    break
                                socket.send(data)
                                bytes += len(data)
                                percentage = (bytes / size) * 100
                                print(f"Enviando... {percentage:.2f}%")
                        break
                    elif userInput == "NAO":
                        response = {"status": "downloadRejected"}
                        socket.send(json.dumps(response).encode())
                        break
                self.isDownloading = False
            else:
                response = {"status": "fileNotFound"}
                socket.send(json.dumps(response).encode())
        except Exception as e:
            print(f"Erro ao processar upload: {str(e)}")
        finally:
            socket.close()
            threading.Thread(target=self.comandosCliente, args=(self.socketServer,)).start()

    def handleRequest(self):
        try:
            downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            downloadSocket.bind(('127.0.0.1', self.clientPort))
            downloadSocket.listen(5)

            # Aceitar request
            clientSocket, _ = downloadSocket.accept()
            threading.Thread(target=self.callUpload, args=(clientSocket,)).start()
        except Exception as e:
            print(f"Erro ao processar a solicitação: {str(e)}")

    def getInput(self):
        try:
            while True:
                if not self.isDownloading:
                    print("Insira algum dos comandos aceitos: \n - SEARCH \n - DOWNLOAD \n")
                    entrada = input().upper()

                    if entrada == "SEARCH":
                        entrada = self.callSearch(self.socketServer)

                    elif entrada == "DOWNLOAD":
                        self.callDownload(self.socketServer)

                    threading.Thread(target=self.comandosCliente, args=(self.socketServer,)).start()
                    break
        except Exception as e:
            print(f"Erro ao processar entrada: {str(e)}")

    def comandosCliente(self, serverSocket):
        threading.Thread(target=self.getInput).start()

    def callDownload(self, serverSocket):
        try:
            arquivo = input("Insira o nome do arquivo que deseja baixar:\n")
            endereco_peer_arquivo = int(input("Insira a porta do peer a partir do qual deseja baixar o arquivo:\n"))

            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerSocket.connect((self.addressServer, endereco_peer_arquivo))

            message = '''{{"method": "DOWNLOAD_REQUEST", "data": {{"filename": "{}", "port": {}}}}}'''.format(arquivo,
                                                                                                              endereco_peer_arquivo)
            peerSocket.sendall(message.encode())

            response = peerSocket.recv(1024).decode()
            data = json.loads(response)

            if data["status"] == "OK":
                file_size = data["fileSize"]
                bytesReceived = 0
                data = b""
                response = peerSocket.recv(1024).decode()
                data = json.loads(response)
                if data["status"] == "downloadAccepted":
                    print("Download do arquivo iniciado")
                    while bytesReceived < file_size:
                        data = peerSocket.recv(1024 * 1024 * 1024)
                        data += data
                        bytesReceived += len(data)
                    filePath = os.path.join(self.folderPeer, arquivo)
                    with open(filePath, "wb") as file:
                        file.write(data)
                    print("Download concluído com sucesso.")

                    arquivos = os.listdir(self.folderPeer)
                    arquivos_formatados = ['"{}"'.format(item) for item in arquivos]
                    arquivos_concatenados = ','.join(arquivos_formatados)
                    message = '''{{"method": "UPDATE", "data": {{"files": [{files}]}}}}'''.format(
                        files=arquivos_concatenados)
                    serverSocket.sendall(message.encode())
                    serverSocket.recv(1024).decode()
                else:
                    print("Download Rejeitado")
            else:
                print("Arquivo não encontrado.")
        except Exception as e:
            print(f"Erro ao processar download: verifique se as informações enviadas estão corretas!")

    def callSearch(self, serverSocket):
        try:
            entrada = input("Insira o arquivo que deseja buscar:\n")
            message = '''{"method":"SEARCH","data":{"query":"%s"}}''' % entrada
            serverSocket.sendall(message.encode())
            print(f"Peers com arquivo solicitado: {serverSocket.recv(1024).decode()} ")
            return entrada
        except Exception as e:
            print(f"Erro ao buscar arquivo: {str(e)}")

    def run(self):
        try:
            threading.Thread(target=self.comandosCliente, args=(self.socketServer,)).start()
            threading.Thread(target=self.handleRequest).start()
            threading.Event().wait()
        finally:
            self.socketServer.close()


# Usage example:
client = P2PClient()
client.setupClient()
client.run()
