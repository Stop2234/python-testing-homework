import string

from ru.hse.OperationResponse import OperationResponse


class Account:
    def __init__(self, login):
        self.storage = None
        self.login = login
        self.active_session = None

    def get_login(self) -> str:
        return self.login

    def get_active_session(self):
        return self.active_session

    def withdraw(self, amount):
        if self.storage is None:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        if self.active_session is None:
            return OperationResponse.NOT_LOGGED_RESPONSE

        response = self.storage.withdraw(self.login, self.active_session, amount)
        if response.code == OperationResponse.CONNECTION_ERROR:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        elif response.code == OperationResponse.INCORRECT_SESSION:
            return OperationResponse.INCORRECT_SESSION_RESPONSE
        elif response.code == OperationResponse.NOT_LOGGED:
            return OperationResponse.NOT_LOGGED_RESPONSE
        elif response.code == OperationResponse.NO_MONEY:
            if isinstance(response.body, float):
                return OperationResponse(OperationResponse.NO_MONEY, response.body)
        elif response.code == OperationResponse.UNDEFINED_ERROR:
            return response
        elif response.code == OperationResponse.SUCCEED:
            if isinstance(response.body, float):
                return OperationResponse(OperationResponse.SUCCEED, response.body)

        return OperationResponse(OperationResponse.INCORRECT_RESPONSE, response)

    def deposit(self, amount):
        if self.storage is None:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        if self.active_session is None:
            return OperationResponse.NOT_LOGGED_RESPONSE

        response = self.storage.deposit(self.login, self.active_session, amount)
        if response.code == OperationResponse.CONNECTION_ERROR:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        elif response.code == OperationResponse.NOT_LOGGED:
            return OperationResponse.NOT_LOGGED_RESPONSE
        elif response.code == OperationResponse.UNDEFINED_ERROR:
            return response
        elif response.code == OperationResponse.SUCCEED:
            if isinstance(response.body, float):
                return OperationResponse(OperationResponse.SUCCEED, response.body)

        return OperationResponse(OperationResponse.INCORRECT_RESPONSE, response)

    def get_balance(self):
        if self.storage is None:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        if self.active_session is None:
            return OperationResponse.NOT_LOGGED_RESPONSE

        response = self.storage.get_balance(self.login, self.active_session)
        if response.code == OperationResponse.CONNECTION_ERROR:
            return OperationResponse.CONNECTION_ERROR_RESPONSE
        elif response.code == OperationResponse.NOT_LOGGED:
            return OperationResponse.NOT_LOGGED_RESPONSE
        elif response.code == OperationResponse.INCORRECT_SESSION:
            return OperationResponse(OperationResponse.INCORRECT_SESSION)
        elif response.code == OperationResponse.UNDEFINED_ERROR:
            return response
        elif response.code == OperationResponse.SUCCEED:
            if isinstance(response.body, float):
                return OperationResponse(OperationResponse.SUCCEED, response.body)

        return OperationResponse(OperationResponse.INCORRECT_RESPONSE, response)

    def init_data_storage(self, accounts_data):
        self.storage = accounts_data