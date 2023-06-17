import socket
import os
import threading
import json

def setupGlobalConfigurations():
    global filesList, socketServer, serverPort, addressServer, clientPort, folderPeer

    filesList = []
    socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverPort = 12346
    addressServer = '127.0.0.1'
    socketServer.connect((addressServer, serverPort))
    clientPort = socketServer.getsockname()[1]
    folderPeer = os.path.join(os.getcwd(), "p2p")


    if not os.path.isdir(folderPeer):
        os.mkdir(folderPeer)

    folderPeer = os.path.join(folderPeer, str(clientPort))
    os.mkdir(folderPeer)


def setupClient(socket):
    print("""                  
 ::::::::    :::        ::::::::::: :::::::::: ::::     ::: :::::::::::  :::::::::: 
++:    +:+   :+:            :+:     :+:        :+:+:    :+:     :+:     :+:        
+            +:+            +:+     +:+        +:+ +:+  +:+     +:+     +:+        
+            +#+            +#+     +#++:++#   +#+  +#+ +#+     +#+     +#++:++   
+            +#+            +#+     +#+        +#+   +#+#+#     +#+     +#+        
+#      +++  #+#            #+#     #+#        #+#    #+#+#     #+#     #+#        
 #########    ########## ########## ########## ###     ####     ###     ########## 

 """)

    print("Está conectando no servidor: " + str(addressServer) + ":" + str(serverPort))
    while True:
        print("Digite 'JOIN' para iniciar.")
        entrada = input()
        if entrada == "JOIN":
            break
    pastaPeer = os.getcwd() + "/p2p/" + str(socketServer.getsockname()[1])
    pathArquivos = pastaPeer
    message = json.dumps({"method": "JOIN", "data": {"filesPath": pathArquivos}})
    socket.sendall(message.encode())

    if socket.recv(1024).decode() == "JOIN_OK":
        arquivos = os.listdir(pastaPeer)
        arquivosFormatados = ['"{}"'.format(item) for item in arquivos]
        arquivosConcatenados = ','.join(arquivosFormatados)
        print(f"Sou o Peer {addressServer}:{clientPort} com arquivos: {arquivosConcatenados}")
    else:
        raise Exception("Falha na Conexao! Programa finalizado.")

def handleDownload(socket):
    request = socket.recv(1024).decode()
    data = json.loads(request)
    filename = data["data"]["filename"]
    peer = data["data"]['port']

    folder = os.path.join(os.path.join(os.getcwd(), "peers"), str(peer))
    if filename in os.listdir(folder):

        path = os.path.join(folder, filename)
        size = os.path.getsize(path)
        response = {"status": "OK", "file_size": size}
        socket.send(json.dumps(response).encode())
        size = os.path.getsize(path) 
        bytes = 0
        sendRate = 1024*1024*10

        with open(path, "rb") as file:
            while True:
                data = file.read(sendRate)
                if not data:
                    break
                socket.send(data)
                bytes += len(data)
                percentage = (bytes / size) * 100
                print(f"Enviando... {percentage:.2f}%")
    else:
        response = {"status": "FILE_NOT_FOUND"}
        socket.send(json.dumps(response).encode())
    socket.close()

def handleRequest():
    downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    downloadSocket.bind(('127.0.0.1', clientPort))
    downloadSocket.listen(5)

    while True:
        clientSocket, _ = downloadSocket.accept()
        threading.Thread(target=handleDownload, args=(clientSocket,)).start()

def comandosCliente(serverSocket, un):
    print("Insira algum dos comandos aceitos: \n - SEARCH \n - DOWNLOAD \n")
    entrada = input().upper()

    if entrada == "SEARCH":
        entrada = input("Insira o arquivo que deseja buscar:\n")
        message = '''{"method":"SEARCH","data":{"query":"%s"}}''' % entrada
        serverSocket.sendall(message.encode())
        print(f"Peers com arquivo solicitado: {serverSocket.recv(1024).decode()} ")

    elif entrada == "DOWNLOAD":
        arquivo = input("Insira o nome do arquivo que deseja baixar:\n")
        endereco_peer_arquivo = int(input("Insira a porta do peer a partir do qual deseja baixar o arquivo:\n"))


        message = '''{{"method": "DOWNLOAD_REQUEST", "data": {{"filename": "{}", "port": {}}}}}'''.format(arquivo, endereco_peer_arquivo)
        serverSocket.sendall(message.encode())
        resposta = serverSocket.recv(1024).decode()

        if resposta =="OK":
            peerClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerClientSocket.connect((addressServer, endereco_peer_arquivo))

            message = '''{{"method": "DOWNLOAD_REQUEST", "data": {{"filename": "{}", "port": {}}}}}'''.format(arquivo, endereco_peer_arquivo)
            peerClientSocket.sendall(message.encode())

            response = peerClientSocket.recv(1024).decode()
            data = json.loads(response)

            if data["status"] == "OK":
                file_size = data["file_size"]
                bytesReceived = 0  
                data = b""  
                print("Download do arquivo iniciado")
                while bytesReceived < file_size:
                    data = peerClientSocket.recv(1024*1024*10)
                    data += data
                    bytesReceived += len(data)
                filePath = os.path.join(folderPeer, arquivo)
                with open(filePath, "wb") as file:
                    file.write(data)
                print("Download concluído com sucesso.")

                arquivos = os.listdir(folderPeer)
                arquivos_formatados = ['"{}"'.format(item) for item in arquivos]
                arquivos_concatenados = ','.join(arquivos_formatados)
                message = '''{{"method": "UPDATE", "data": {{"files": [{files}]}}}}'''.format(files=arquivos_concatenados)
                serverSocket.sendall(message.encode())
                print(serverSocket.recv(1024).decode())
            else:
                print("Arquivo não encontrado.")

        else:
            print("Arquivo não autorizado")

    threading.Thread(target=comandosCliente, args=(serverSocket, serverSocket)).start()

def run():
    try:
        threading.Thread(target=handleRequest).start()
        threading.Thread(target=comandosCliente, args=(socketServer, socketServer)).start()
        threading.Event().wait()
    finally:
        socketServer.close()

setupGlobalConfigurations()
setupClient(socketServer)
run()


