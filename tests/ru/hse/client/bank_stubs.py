"""Simple, stateful test doubles for the bank's authorization and account-data sources.

They implement the contracts from the task specification, not the real HTTP API.
A method's ``*_error`` option simulates a particular source failure without
changing stored funds. All balances returned to Account are floating-point.
"""

from ru.hse.OperationResponse import OperationResponse


class BankStub:
    def __init__(self, authorization, data, *, initial_balance=0.0, session=1,
                 balance_error=None, deposit_error=None, withdraw_error=None):
        self.balance = float(initial_balance)
        self.session = session
        self.active = False
        self.balance_error = balance_error
        self.deposit_error = deposit_error
        self.withdraw_error = withdraw_error

        authorization.login.side_effect = self.login
        authorization.register.side_effect = self.register
        authorization.logout.side_effect = self.logout
        data.get_balance.side_effect = self.get_balance
        data.deposit.side_effect = self.deposit
        data.withdraw.side_effect = self.withdraw

    def register(self, login, password):
        return self.login(login, password)

    def login(self, login, password):
        if self.active:
            return OperationResponse(OperationResponse.ALREADY_LOGGED, self.session)
        self.active = True
        return OperationResponse(OperationResponse.SUCCEED, self.session)

    def logout(self, login, session):
        if not self.active:
            return OperationResponse(OperationResponse.NOT_LOGGED)
        if session != self.session:
            return OperationResponse(OperationResponse.INCORRECT_SESSION)
        self.active = False
        return OperationResponse(OperationResponse.SUCCEED)

    def _check_access(self, session):
        if not self.active:
            return OperationResponse(OperationResponse.NOT_LOGGED)
        if session != self.session:
            return OperationResponse(OperationResponse.INCORRECT_SESSION)
        return None

    def get_balance(self, login, session):
        problem = self._check_access(session)
        if problem is not None:
            return problem
        if self.balance_error is not None:
            return OperationResponse(self.balance_error)
        return OperationResponse(OperationResponse.SUCCEED, self.balance)

    def deposit(self, login, session, delta):
        problem = self._check_access(session)
        if problem is not None:
            return problem
        if self.deposit_error is not None:
            return OperationResponse(self.deposit_error)
        self.balance += delta
        return OperationResponse(OperationResponse.SUCCEED, self.balance)

    def withdraw(self, login, session, delta):
        problem = self._check_access(session)
        if problem is not None:
            return problem
        if self.withdraw_error is not None:
            return OperationResponse(self.withdraw_error)
        if delta > self.balance:
            return OperationResponse(OperationResponse.NO_MONEY, self.balance)
        self.balance -= delta
        return OperationResponse(OperationResponse.SUCCEED, self.balance)


class DataStub(BankStub):
    """Only the data-source part, for tests that instantiate Account directly."""

    def __init__(self, data, **kwargs):
        from unittest.mock import Mock
        self._authorization = Mock()
        super().__init__(self._authorization, data, **kwargs)
        self.active = True
