import base64
import pickle
from typing import Any, Optional, Union

import javaobj
from javaobj import load
from io import BytesIO

from javaobj.v2.transformers import JavaInt


class OperationResponse:
    # Константы кодов
    SUCCEED = 0
    ALREADY_LOGGED = 1
    NOT_LOGGED = 2
    NO_USER_INCORRECT_PASSWORD = 3
    INCORRECT_RESPONSE = 4
    UNDEFINED_ERROR = 5
    INCORRECT_SESSION = 6
    NO_MONEY = 7
    ENCODING_ERROR = 8
    ALREADY_INITIATED = 9
    NULL_ARGUMENT = 10
    CONNECTION_ERROR = 11

    # Предопределенные экземпляры
    ACCOUNT_MANAGER_RESPONSE = None
    NO_USER_INCORRECT_PASSWORD_RESPONSE = None
    UNDEFINED_ERROR_RESPONSE = None
    NOT_LOGGED_RESPONSE = None
    INCORRECT_SESSION_RESPONSE = None
    SUCCEED_RESPONSE = None
    NO_MONEY_RESPONSE = None
    ENCODING_ERROR_RESPONSE = None
    ALREADY_INITIATED_RESPONSE = None
    NULL_ARGUMENT_EXCEPTION = None
    CONNECTION_ERROR_RESPONSE = None

    def __init__(self, code: int, body: Any = None):
        self.code = code
        self.body = body

    def to_result_string(self) -> str:
        sb = str(self.code)
        if self.body is not None:
            if isinstance(self.body, OperationResponse):
                sb += "|3|" + self.body.to_result_string()
            elif isinstance(self.body, str):
                sb += "|1|" + self.body
            else:
                sb += "|2|" + self._response_to_string(self.body)
        return sb

    @classmethod
    def from_string(cls, string: str) -> 'OperationResponse':
        ind = string.find("|")
        try:
            if ind > -1:
                code = int(string[:ind])
                string = string[ind+1:]
                ind = string.find("|")
                mode = int(string[:ind])
                if mode == 1:
                    return OperationResponse(code, string[ind+1:])
                elif mode == 2:
                    return OperationResponse(code, cls._response_from_string(string[ind+1:]))
                elif mode == 3:
                    return OperationResponse(code, cls.from_string(string[ind+1:]))

            code = int(string)
            if code >= 0:
                return OperationResponse(code, None)
        except (ValueError, Exception):
            pass

        return OperationResponse(cls.UNDEFINED_ERROR, string)

    @classmethod
    def code_to_error_message(cls, code: int) -> str:
        messages = {
            cls.SUCCEED: "SUCCEED",
            cls.ALREADY_LOGGED: "ALREADY LOGGED OR REGISTERED",
            cls.NOT_LOGGED: "NOT LOGGED",
            cls.NO_USER_INCORRECT_PASSWORD: "INCORRECT PASSWORD OR NO SUCH USER",
            cls.INCORRECT_RESPONSE: "INCORRECT RESPONCE",
            cls.UNDEFINED_ERROR: "UNDEFINED ERROR",
            cls.INCORRECT_SESSION: "INCORRECT SESSION NUMBER",
            cls.NO_MONEY: "NOT ENOUGH MONEYS ON BALANCE",
            cls.ENCODING_ERROR: "ENCODING CANNOT BE MADE",
            cls.ALREADY_INITIATED: "ACCOUNT WAS ALREADY INITIATED",
            cls.NULL_ARGUMENT: "Null argument is prohibited",
            cls.CONNECTION_ERROR: "No connection to server"
        }
        return messages.get(code, f"CODE_{code}")

    def __str__(self) -> str:
        sb = self.code_to_error_message(self.code)
        if self.body is not None:
            sb += f"[{str(self.body)}]"
        return sb

    @staticmethod
    def _response_to_string(obj: Any) -> str:
        try:
            serialized = pickle.dumps(obj)
            return base64.b64encode(serialized).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Serialization error: {e}")

    @staticmethod
    def _response_from_string(string: str) -> Any:
        try:
            data = base64.b64decode(string)
            file_like = BytesIO(data)
            java_obj = load(file_like)
            return java_obj.value
        except Exception as e:
            raise RuntimeError(f"Deserialization error: {e}")

# Инициализация статических экземпляров после определения класса
OperationResponse.ACCOUNT_MANAGER_RESPONSE = OperationResponse(OperationResponse.ALREADY_LOGGED, None)
OperationResponse.NO_USER_INCORRECT_PASSWORD_RESPONSE = OperationResponse(OperationResponse.NO_USER_INCORRECT_PASSWORD, None)
OperationResponse.UNDEFINED_ERROR_RESPONSE = OperationResponse(OperationResponse.UNDEFINED_ERROR, None)
OperationResponse.NOT_LOGGED_RESPONSE = OperationResponse(OperationResponse.NOT_LOGGED, None)
OperationResponse.INCORRECT_SESSION_RESPONSE = OperationResponse(OperationResponse.INCORRECT_SESSION, None)
OperationResponse.SUCCEED_RESPONSE = OperationResponse(OperationResponse.SUCCEED, None)
OperationResponse.NO_MONEY_RESPONSE = OperationResponse(OperationResponse.NO_MONEY, None)
OperationResponse.ENCODING_ERROR_RESPONSE = OperationResponse(OperationResponse.ENCODING_ERROR, None)
OperationResponse.ALREADY_INITIATED_RESPONSE = OperationResponse(OperationResponse.ALREADY_INITIATED, None)
OperationResponse.NULL_ARGUMENT_EXCEPTION = OperationResponse(OperationResponse.NULL_ARGUMENT, None)
OperationResponse.CONNECTION_ERROR_RESPONSE = OperationResponse(OperationResponse.CONNECTION_ERROR, None)