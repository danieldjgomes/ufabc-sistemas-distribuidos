import socket
import json
import threading
import os


def doUpdate(listOfPeers, c, addr, data):
    if 'data' in data and 'files' in data['data']:
        files = data['data']['files']
        listOfPeers[addr[1]] = files
        c.sendall(b'UPDATE_OK')
    else:
        print("Invalid JSON structure or missing required fields.")
   
def doSearch(listOfPeers, c, data):
    search = data['data']['query']
    result = []
    for key, values in listOfPeers.items():
        if search in values:
            result.append(key)
    c.sendall(str(result).encode())

def doJoin(listOfPeers, c, addr, data):
    files = data['data']['filesPath']
    listOfPeers[addr[1]] = os.listdir(files)
    print("Peer {}:{} adicionado com os arquivos {}".format(addr[0],addr[1],os.listdir(files)))
    c.send(b'JOIN_OK')

def receiveData(c):
    data = ""
    while True:
        try:
            received = c.recv(1024)
            data += received.decode()
        except:
            return data
        else:
            return data

listOfPeers = dict()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12346
s.bind(('127.0.0.1',port))

print(
    """
 ::::::::  :::::::::: :::::::::  :::     ::: ::::::::::: :::::::::   ::::::::  :::::::::  
:+:    :+: :+:        :+:    :+: :+:     :+:     :+:     :+:    :+: :+:    :+: :+:    :+: 
+:+        +:+        +:+    +:+ +:+     +:+     +:+     +:+    +:+ +:+    +:+ +:+    +:+ 
+#++:++#++ +#++:++#   +#++:++#:  +#+     +:+     +#+     +#+    +:+ +#+    +:+ +#++:++#:  
       +#+ +#+        +#+    +#+  +#+   +#+      +#+     +#+    +#+ +#+    +#+ +#+    +#+ 
#+#    #+# #+#        #+#    #+#   #+#+#+#       #+#     #+#    #+# #+#    #+# #+#    #+# 
 ########  ########## ###    ###     ###     ########### #########   ########  ###    ### 
    """
)
print("-------------------------------------------------")
print("Servidor rodando no endereço 127.0.0.1:%s" %(port))
s.listen(1)

        
def run(doUpdate, doSearch, doJoin, receiveData, listOfPeers, c, addr):
    c.settimeout(2)
    print('Connected: ', addr)
    
    while True:
        call = receiveData(c)

        try:
            if(call != ""):
                data = json.loads(call)

                if(data['method'] == "JOIN"):
                    threading.Thread(target=doJoin, args=(listOfPeers, c, addr, data)).start()

                if(data['method'] == "SEARCH"):
                    threading.Thread(target=doSearch, args=(listOfPeers, c, data)).start()
                
                if(data['method'] == "UPDATE"):
                    threading.Thread(target=doUpdate, args=(listOfPeers, c, addr, data)).start()                

        except json.JSONDecodeError as e:
            print("Error decoding JSON data:", str(e))

while True:
    c, addr = s.accept()
    threading.Thread(target=run, args=(doUpdate, doSearch, doJoin, receiveData, listOfPeers, c, addr)).start()