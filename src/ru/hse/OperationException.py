class OperationException(Exception):
    def __init__(self, resp):
        self.response = resp

    def to_result_string(self):
        return self.response.to_result_string()

    def __str__(self):
        return str(self.response)