import atexit
import threading
from threading import Lock
import collections
from typing import Dict


from ru.hse.Account import Account
from ru.hse.IAccountDataSource import IAccountDataSource
from ru.hse.IAuthorizationSource import IAuthorizationSource
from ru.hse.OperationException import OperationException
from ru.hse.OperationResponse import OperationResponse
from collections import deque
from threading import Lock
from typing import Collection, Optional


class AccountManager:
    def __init__(self, serv: IAuthorizationSource, server_accounts_data: IAccountDataSource):
        self.server_auth_data = None
        self.server_accounts_data = None
        self.exceptions_list = deque()
        self.accounts_lock = Lock()
        self.exceptions_lock = Lock()
        self.active_accounts = {}
        self.init(serv, server_accounts_data)

    @staticmethod
    def get_encoded_password(password: str) -> Optional[str]:
        return f"encoded_{password}" if password else None

    def init(self, auth_source: IAuthorizationSource, data_source: IAccountDataSource):
        if self.server_auth_data or self.server_accounts_data:
            raise OperationException(OperationResponse(code=OperationResponse.ALREADY_INITIATED))
        if not auth_source or not data_source:
            raise OperationException(OperationResponse(code=OperationResponse.NULL_ARGUMENT))
        self.server_auth_data = auth_source
        self.server_accounts_data = data_source

    def register(self, login: str, password: str) -> Optional[Account]:
        if not login or not password:
            self.register_exception(OperationException(OperationResponse(code=OperationResponse.NULL_ARGUMENT)))
            return None

        with self.accounts_lock:
            active_account = self.active_accounts.get(login)
            if active_account:
                self.register_exception(OperationException(OperationResponse(code=OperationResponse.ALREADY_INITIATED)))
                return None

            hashed = self.get_encoded_password(password)
            response = self.call_register(login, hashed)
            if response.code == OperationResponse.SUCCEED:
                account = response.body
                self.active_accounts[login] = account
                return account
            else:
                match response.code:
                    case OperationResponse.CONNECTION_ERROR | \
                         OperationResponse.UNDEFINED_ERROR | \
                         OperationResponse.INCORRECT_RESPONSE | \
                         OperationResponse.ALREADY_LOGGED:
                        self.register_exception(OperationException(response))
                    case _:
                        self.register_exception(OperationException(OperationResponse.INCORRECT_RESPONSE, response))
            return None

    def login(self, login: str, password: str) -> Optional[Account]:
        if not login or not password:
            self.register_exception(OperationException(OperationResponse(code=OperationResponse.NULL_ARGUMENT)))
            return None

        with self.accounts_lock:
            active_account = self.active_accounts.get(login)
            if active_account:
                self.register_exception(OperationException(OperationResponse(code=OperationResponse.ALREADY_LOGGED, body=active_account.active_session)))
                return None

            hashed = self.get_encoded_password(password)
            response = self.call_login(login, hashed)
            if response.code == OperationResponse.SUCCEED:
                account = response.body
                self.active_accounts[login] = account
                return account
            else:
                match response.code:
                    case OperationResponse.CONNECTION_ERROR | \
                         OperationResponse.UNDEFINED_ERROR| \
                         OperationResponse.NO_USER_INCORRECT_PASSWORD | \
                         OperationResponse.INCORRECT_RESPONSE | \
                         OperationResponse.ALREADY_LOGGED:
                        self.register_exception(OperationException(response))
                    case _:
                        self.register_exception(OperationException(OperationResponse.INCORRECT_RESPONSE, response))
            return None

    def call_register(self, login: str, password: str) -> OperationResponse:
        response = self.server_auth_data.register(login, password)
        if response.code == OperationResponse.SUCCEED:
            answer = response.body
            if answer and isinstance(answer, int):  # Assuming int instead of Long
                account = Account(login)
                account.active_session = answer
                account.init_data_storage(self.server_accounts_data)
                return OperationResponse(code=OperationResponse.SUCCEED, body=account)
        else:
            match response.code:
                case OperationResponse.CONNECTION_ERROR | \
                     OperationResponse.UNDEFINED_ERROR | \
                     OperationResponse.ALREADY_INITIATED:
                    return response
                case _:
                    return OperationResponse(code=OperationResponse.INCORRECT_RESPONSE, body=response)
        return OperationResponse(code=OperationResponse.INCORRECT_RESPONSE, body=response)

    def call_login(self, login: str, password: str) -> OperationResponse:
        response = self.server_auth_data.login(login, password)
        if response.code == OperationResponse.SUCCEED:
            answer = response.body
            if isinstance(answer, int):
                account = Account(login)
                account.active_session = answer
                account.init_data_storage(self.server_accounts_data)
                return OperationResponse(code=OperationResponse.SUCCEED, body=account)
        else:
            match response.code:
                case OperationResponse.CONNECTION_ERROR | \
                     OperationResponse.UNDEFINED_ERROR | \
                     OperationResponse.NO_USER_INCORRECT_PASSWORD | \
                     OperationResponse.ALREADY_LOGGED:
                    return response
                case _:
                    return OperationResponse(code=OperationResponse.INCORRECT_RESPONSE, body=response)

    def call_logout(self, account: Account) -> OperationResponse:
        if not account.get_active_session():
            return OperationResponse(code=OperationResponse.NOT_LOGGED)
        response = self.server_auth_data.logout(account.get_login(), account.get_active_session())
        match response.code:
            case OperationResponse.SUCCEED | \
                 OperationResponse.CONNECTION_ERROR | \
                 OperationResponse.UNDEFINED_ERROR | \
                 OperationResponse.NOT_LOGGED | \
                 OperationResponse.INCORRECT_SESSION:
                return response
            case _:
                return OperationResponse(code=OperationResponse.INCORRECT_RESPONSE, body=response)

    def logout(self, account: Account) -> bool:
        if not account or not account.get_login():
            self.register_exception(OperationException(OperationResponse(code=OperationResponse.NULL_ARGUMENT)))
            return False
        active_account = self.active_accounts.get(account.get_login())
        if not active_account:
            self.register_exception(OperationException(OperationResponse(code=OperationResponse.NOT_LOGGED)))
            return False
        response = self.call_logout(active_account)
        if response.code == OperationResponse.SUCCEED:
            del self.active_accounts[account.get_login()]
            return True
        else:
            match response.code:
                case OperationResponse.CONNECTION_ERROR | \
                     OperationResponse.UNDEFINED_ERROR | \
                     OperationResponse.NOT_LOGGED | \
                     OperationResponse.INCORRECT_SESSION | \
                     OperationResponse.INCORRECT_RESPONSE:
                    self.register_exception(OperationException(response))
                case _:
                    self.register_exception(OperationException(code=OperationResponse.INCORRECT_RESPONSE, body=response))
        return False

    def register_exception(self, exception: OperationException):
        with self.exceptions_lock:
            self.exceptions_list.append(exception)

    def get_exceptions(self) -> Collection[OperationException]:
        with self.exceptions_lock:
            return list(self.exceptions_list)  # Return a copy to avoid modification
