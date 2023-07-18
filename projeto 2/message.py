import json

class Message:
    def __init__(self, method, key, value):
        self.key = key
        self.method = method
        self.value = value

    def __str__(self):
        return f"Mensagem: method={self.method}, key={self.key} value={self.value}"

    def to_json(self):
        return {
            "method": self.method,
            "key": self.key,
            "value": self.value
        }

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        return cls(json_data["method"], json_data["key"], json_data["value"])
