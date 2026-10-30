from abc import ABC, abstractmethod

from ru.hse.OperationResponse import OperationResponse


class IAuthorizationSource(ABC):
    @abstractmethod
    def register(self, login: str, password: str) -> OperationResponse:
        pass

    @abstractmethod
    def login(self, login: str, password: str) -> OperationResponse:
        pass

    @abstractmethod
    def logout(self, login: str, active_session: int) -> OperationResponse:
        pass