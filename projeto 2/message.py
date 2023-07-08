class Message:
    def __init__(self, method, value):
        self.method = method
        self.value = value

    def __str__(self):
        return f"Message: method={self.method}, value={self.value}"

    def to_json(self):
        return {
            "method": self.method,
            "value": self.value
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["method"], json_data["value"])
    