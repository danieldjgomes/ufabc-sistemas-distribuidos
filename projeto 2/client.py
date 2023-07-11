import socket
import json
import random
import time
from message import Message


class Client:
    def __init__(self):
        self.servers = [('127.0.0.1', 10097), ('127.0.0.1', 10098), ('127.0.0.1', 10099)]
        # self.servers = [('127.0.0.1', 10097)]
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
            print(f"Error occurred while sending request: {e}")
            

    def run(self):
        while True:
            self.chooseServer()
            print("Server escolhido: ", self.server)
            print("Options:")
            print("1. PUT")
            print("2. GET")
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")

            if choice == "1":
                key = input("Enter the key: ")
                value = input("Enter the value: ")
                response = self.sendRequest(Message("PUT", key, (value, None)))
                print("PUT_OK" if response == "PUT_OK" else "Error occurred during PUT operation")

            elif choice == "2":
                key = input("Enter the key: ")
                response = self.sendRequest(Message("GET", key, int(time.time())))
                if response["method"] == "NULL":
                    print("Key not found")
                elif response["method"] == "TRY_OTHER_SERVER_OR_LATER":
                    print("Try other server or request later")
                else:
                    print(f"Value: {response})")

            elif choice == "3":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


# Run the client
client = Client()
client.run()
