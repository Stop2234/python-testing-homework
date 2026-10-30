from ru.hse.OperationException import OperationException
from ru.hse.OperationResponse import OperationResponse
from ru.hse.client.AccountManager import AccountManager
from ru.hse.client.ApiClient import ApiClient


class Client:
    def __init__(self, auth_source, data_source):
        if isinstance(auth_source, str) and data_source is None:
            base_api_client = ApiClient(auth_source)
            self.account_manager = AccountManager(base_api_client, base_api_client)
        else:
            self.account_manager = AccountManager(auth_source, data_source)

    # Для тестов только, не использовать в производственном коде
    def get_account_manager(self):
        return self.account_manager

    def register(self, login, password):
        size = len(self.account_manager.get_exceptions())
        account = self.account_manager.register(login, password)
        if account is None:
            exs = self.account_manager.get_exceptions()[size:]
            for oe in exs:
                if oe.response.code in [
                    OperationResponse.NULL_ARGUMENT,
                    OperationResponse.ALREADY_INITIATED,
                    OperationResponse.UNDEFINED_ERROR,
                    OperationResponse.CONNECTION_ERROR
                ]:
                    raise oe
                else:
                    print(oe)
        return account

    def login(self, login, password):
        size = len(self.account_manager.get_exceptions())
        account = self.account_manager.login(login, password)
        if account is None:
            exs = self.account_manager.get_exceptions()[size:]
            for oe in exs:
                if oe.response.code in [
                    OperationResponse.NULL_ARGUMENT,
                    OperationResponse.UNDEFINED_ERROR,
                    OperationResponse.CONNECTION_ERROR,
                    OperationResponse.ALREADY_LOGGED,
                    OperationResponse.NO_USER_INCORRECT_PASSWORD
                ]:
                    raise oe
                else:
                    print(oe)
        return account

    def logout(self, account):
        size = len(self.account_manager.get_exceptions())
        result = self.account_manager.logout(account)
        if not result:
            exs = self.account_manager.get_exceptions()[size:]
            for oe in exs:
                if oe.response.code in [
                    OperationResponse.UNDEFINED_ERROR,
                    OperationResponse.NULL_ARGUMENT,
                    OperationResponse.NOT_LOGGED,
                    OperationResponse.INCORRECT_SESSION,
                    OperationResponse.CONNECTION_ERROR
                ]:
                    raise oe
                else:
                    print(oe)
        return result

    @staticmethod
    def get_balance(account):
        response = account.get_balance()
        if response.code == OperationResponse.SUCCEED:
            return response.body
        if response.code == OperationResponse.INCORRECT_RESPONSE:
            print(response)
        else:
            raise OperationException(response)
        return float('nan')

    @staticmethod
    def withdraw(account, amount):
        response = account.withdraw(amount)
        if response.code == OperationResponse.SUCCEED:
            return response.body
        if response.code == OperationResponse.INCORRECT_RESPONSE:
            print(response)
        else:
            raise OperationException(response)
        return float('nan')

    @staticmethod
    def deposit(account, amount):
        response = account.deposit(amount)
        if response.code == OperationResponse.SUCCEED:
            return response.body
        if response.code == OperationResponse.INCORRECT_RESPONSE:
            print(response)
        else:
            raise OperationException(response)
        return float('nan')