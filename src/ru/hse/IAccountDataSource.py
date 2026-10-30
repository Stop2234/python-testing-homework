from abc import ABC, abstractmethod

from ru.hse.OperationResponse import OperationResponse


class IAccountDataSource(ABC):
    @abstractmethod
    def withdraw(self, login: str, session: int, balance: float) -> OperationResponse:
        pass

    @abstractmethod
    def deposit(self, login: str, session: int, balance: float) -> OperationResponse:
        pass

    @abstractmethod
    def get_balance(self, login: str, session: int) -> OperationResponse:
        pass