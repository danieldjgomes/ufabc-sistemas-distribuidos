import socket
import json
import random
from message import Message


class Client:
    def __init__(self):
        self.servers = [('127.0.0.1', 10097), ('127.0.0.1', 10098), ('127.0.0.1', 10099)]
        self.server = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def chooseServer(self):
        self.server = random.choice(self.servers)

    def sendRequest(self, method, key=None, value=None):
        message = Message(method, key=key, value=value)
        try:
            self.socket.connect(self.server)
            self.socket.sendall(json.dumps(message.to_json()).encode())
            response = self.socket.recv(1024).decode()
            return json.loads(response)
        except Exception as e:
            print(f"Error occurred while sending request: {e}")
        finally:
            self.socket.close()

    def run(self):
        self.chooseServer()

        while True:
            print("Options:")
            print("1. PUT")
            print("2. GET")
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")

            if choice == "1":
                key = input("Enter the key: ")
                value = input("Enter the value: ")
                response = self.sendRequest("PUT", key=key, value=value)
                print("PUT_OK" if response == "PUT_OK" else "Error occurred during PUT operation")

            elif choice == "2":
                key = input("Enter the key: ")
                timestamp = input("Enter the timestamp: ")
                response = self.sendRequest("GET", key=key, timestamp=timestamp)
                if response == "NULL":
                    print("Key not found")
                elif response == "TRY_OTHER_SERVER_OR_LATER":
                    print("Try other server or request later")
                else:
                    print(f"Value: {response['value']}, Timestamp: {response['timestamp']}")

            elif choice == "3":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


# Run the client
client = Client()
client.run()
