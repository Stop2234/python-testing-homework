from contextlib import closing
from urllib.parse import urlencode

import requests

from ru.hse.IAccountDataSource import IAccountDataSource
from ru.hse.IAuthorizationSource import IAuthorizationSource
from ru.hse.OperationResponse import OperationResponse


class ApiClient (IAccountDataSource, IAuthorizationSource):
    def __init__(self, url):
        self.connection_uri = url

    def withdraw(self, login: str, session: int, balance: float) -> OperationResponse:
        # Формируем JSON-тело запроса (используем словарь для гарантии корректности)
        json_body = {
            "login": login,
            "session": session,
            "amount": balance
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                f"{self.connection_uri}/account/withdraw",
                json=json_body,
                headers=headers
            )
            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))


    def deposit(self, login, session, amount):
        json_body = {
            "login": login,
            "session": session,
            "amount": amount
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                f"{self.connection_uri}/account/deposit",
                json=json_body,
                headers=headers
            )
            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))

    def get_balance(self, login, session):
        json_body = {
            "login": login,
            "session": session
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                f"{self.connection_uri}/account/balance",
                json=json_body,
                headers=headers
            )
            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))

    def register(self, login: str, password: str) -> OperationResponse:
        data = {"login": login, "password": password}
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                f"{self.connection_uri}/register",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))

    def login(self, login: str, password: str) -> OperationResponse:
        data = {"login": login, "password": password}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(
                f"{self.connection_uri}/login",
                json=data,
                headers=headers
            )

            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))

    def logout(self, login, active_session):
        json_body = {
            "login": login,
            "session": active_session
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(
                f"{self.connection_uri}/account/logout",
                json=json_body,
                headers=headers
            )

            response.raise_for_status()
            return OperationResponse.from_string(response.text)
        except requests.ConnectionError as ce:
            return OperationResponse(OperationResponse.CONNECTION_ERROR, str(ce))
        except Exception as e:
            return OperationResponse(OperationResponse.UNDEFINED_ERROR, str(e))