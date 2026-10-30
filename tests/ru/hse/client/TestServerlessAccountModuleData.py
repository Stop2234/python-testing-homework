from bank_stubs import DataStub
import math

import pytest
from unittest import mock

from ru.hse.Account import Account
from ru.hse.IAccountDataSource import IAccountDataSource
from ru.hse.OperationResponse import OperationResponse


class TestServerlessAccountModuleData:
    def setup_method(self):
        self.data_source = mock.create_autospec(IAccountDataSource)

    def test_deposit_no_source(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        delta_correct = 100.0
        account = Account(correct_login)
        account.active_session = correct_session

        #act
        response = account.deposit(delta_correct)

        #assert
        assert response is not None, "Deposit function return is null for connection error"
        assert response.code == OperationResponse.CONNECTION_ERROR, "Error code incorrect during deposit"
        assert response.body is None, "Body should be null for connection error"

    def test_deposit_success(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        delta_correct = 100.0

        #record
        DataStub(self.data_source)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)  # Метод инициализации dataSource, возможно другой название
        account.active_session = correct_session

        #act
        response = account.deposit(delta_correct)

        #assert
        assert response is not None, "Response is null for correct deposit"
        assert response.code == OperationResponse.SUCCEED, "Response code is not succeed for correct deposit"
        assert response.body is not None, "Response data field is null for correct deposit"
        assert isinstance(response.body, float), "Response data field value has incorrect type for correct deposit"
        assert math.isclose(response.body, delta_correct,
                            rel_tol=1e-3), "Returned balance after correct deposit is not equal to value added by deposit"

    # Для параметраризованных тестов:
    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR,
    ])
    def test_deposit_exceptions(self, exception_code):
        #arrange
        correct_login = "user"
        correct_session = 1
        delta_correct = 100.0

        #record
        DataStub(self.data_source, deposit_error=exception_code)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session

        #act
        response = account.deposit(delta_correct)

        #assert
        code_message = OperationResponse.code_to_error_message(exception_code)
        assert response is not None, f"Response is null on deposit with system code({code_message})"
        assert response.code == exception_code, f"Response return value is not expected system code for incorrect deposit ({code_message})"
        assert response.body is None, f"Reponse data field is not null for server code where it needs to be so({code_message})"

    def test_withdraw_no_source(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        delta_withdraw = 100.0
        account = Account(correct_login)
        account.active_session = correct_session  # Здесь может быть ошибка, если session не инициализирована корректно

        #act
        response = account.withdraw(delta_withdraw)

        #assert
        assert response is not None, "Response is not null for withdraw on not connected account"
        assert response.code == OperationResponse.CONNECTION_ERROR, "Response code is not connection error for not connected account and withdraw call"
        assert response.body is None, "Response code is not null for withdraw on not connected account"

    def test_withdraw_no_money(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        init_balance = 50.0
        delta_too_much_withdraw = 100.0

        #record
        DataStub(self.data_source, initial_balance=init_balance)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session

        # Act
        response = account.withdraw(delta_too_much_withdraw)

        # Assert
        assert response is not None, "Response is null for too-much call on withdraw"
        assert response.code == OperationResponse.NO_MONEY, "Response code is not NO_MONEY for too-much withdraw call"
        assert math.isclose(response.body, init_balance,
                            rel_tol=1e-3), "Response data is not a start balance for NO_MONEY on too-much withdraw"

    def test_withdraw_success(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        init_balance = 100.0
        delta_correct_deposit = 100.0
        delta_correct_withdraw = 100.0

        #record
        DataStub(self.data_source)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session
        account.deposit(delta_correct_deposit)

        #act
        response = account.withdraw(delta_correct_withdraw)

        #assert
        assert response is not None, "Response is null for correct withdraw"
        assert response.code == OperationResponse.SUCCEED, "Response code is not Succeed for correct withdraw"
        assert response.body is not None, "Response data is null when it needs to be not-null for correct withdraw"
        assert isinstance(response.body, float), "Response data type is not Double as expected for correct withdraw"
        assert math.isclose(response.body, delta_correct_deposit - delta_correct_withdraw, rel_tol=1e-3), \
            "Withdraw result is not equal to deposit-withdraw for correct withdraw"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR
    ])
    def test_withdraw_exceptions(self, exception_code):
        #arrange
        correct_login = "user"
        correct_session = 1
        init_balance = 50.0
        delta_correct_withdraw = 100.0

        #record
        DataStub(self.data_source, withdraw_error=exception_code)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session

        #act
        response = account.withdraw(delta_correct_withdraw)

        #assert
        assert response is not None, (
            f"Response is null for withdraw with server code ({OperationResponse.code_to_error_message(exception_code)})"
        )
        assert response.code == exception_code, (
            f"Response code is not equal to server code for withdraw with server code ({OperationResponse.code_to_error_message(exception_code)})"
        )
        assert response.body is None, (
            f"Withdraw result body not null for server code {OperationResponse.code_to_error_message(exception_code)}"
        )

    def test_get_balance_no_source(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        account = Account(correct_login)
        account.active_session = correct_session

        #act
        response = account.get_balance()

        #assert
        assert response is not None, (
            "Response is null for getBalance on not connected account"
        )
        assert response.code == OperationResponse.CONNECTION_ERROR, (
            f"Expected CONNECTION_ERROR but got Connection error in getBalance test"
        )
        assert response.body is None, (
            "Response data body should be None when no dataSource initialized"
        )

    def test_get_balance_success(self):
        #arrange
        correct_login = "user"
        correct_session = 1
        init_balance = 50.0

        #record
        DataStub(self.data_source, initial_balance=init_balance)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session

        #act
        response = account.get_balance()

        assert response is not None, "Response is null for correct getBalance"
        assert response.code == OperationResponse.SUCCEED, "Response code is not succeed for correct getBalance"
        assert response.body is not None, "Response data is null where it needs to be not null for correct getBalance"
        assert isinstance(response.body, float), "Response data have incorrect type for correct getBalance"
        assert math.isclose(response.body, init_balance,
                            rel_tol=1e-3), "Response data is not equal to balance according to correct getBalance"

    # Параметризованный тест для проверки исключений
    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR
    ])
    def test_get_balance_exceptions(self, exception_code):
        #arrange
        correct_login = "user"
        correct_session = 1
        init_balance = 50.0

        #record
        DataStub(self.data_source, balance_error=exception_code)

        #arrange_2
        account = Account(correct_login)
        account.init_data_storage(self.data_source)
        account.active_session = correct_session

        #act
        response = account.get_balance()

        #assert
        assert response is not None, f"Response is null for getBalance with server code {OperationResponse.code_to_error_message(exception_code)}"
        assert response.code == exception_code, f"Response code is not equal to server code for getBalance with server code ({OperationResponse.code_to_error_message(exception_code)})"
        assert response.body is None, f"Response data is not null for getBalance with server code ({OperationResponse.code_to_error_message(exception_code)})"

    def test_account_get_login(self):
        #arrange
        correct_login = "user"

        #act
        account = Account(correct_login)

        #assert
        assert correct_login == account.get_login(), "account login is not equal to passed throw constructor"
