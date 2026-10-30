from bank_stubs import BankStub

import pytest
from unittest import mock

from ru.hse.OperationException import OperationException
from ru.hse.client.Client import Client
from ru.hse.client.AccountManager import AccountManager
from ru.hse.IAccountDataSource import IAccountDataSource
from ru.hse.IAuthorizationSource import IAuthorizationSource
from ru.hse.OperationResponse import OperationResponse


class TestServerlessClientIntegrationData:
    def setup_method(self):
        self.data_source = mock.create_autospec(IAccountDataSource)
        self.auth_source = mock.create_autospec(IAuthorizationSource)

    def test_client_get_balance_correct_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0

        #record (имитируем поведение)
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        #act
        ret_balance = Client.get_balance(a)  # сохраняем оригинальное имя метода getBalance в camelCase как есть

        #assert (сохраняем оригинальный текст)
        assert start_balance == ret_balance, "Start balance not equal to expected one"

    def test_client_get_balance_local_not_logged_exceptions(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0

        #record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)

        #act & assert (сохраняем оригинальный текст с Java-шаблонами)
        with pytest.raises(OperationException) as excinfo:
            Client.get_balance(
                a), "Exception not thrown for getBalance after some server code(" + OperationResponse.code_to_error_message(
                OperationResponse.NOT_LOGGED) + ")"
        exc = excinfo.value

        #assert (сохраняем оригинальный текст)
        assert exc.response is not None, "Exception responce is null during incorrect getBalance"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "Exception code is not relevant to server answer during incorrect getBalance"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR
    ])
    def test_client_get_balance_exceptions(self, exception_code):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0

        #record
        BankStub(self.auth_source, self.data_source, balance_error=exception_code)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        #act & assert (сохраняем оригинальный текст с Java-шаблонами и параметризацию)
        with pytest.raises(OperationException) as excinfo:
            Client.get_balance(
                a), "Exception not thrown for getBalance after some server code(" + OperationResponse.code_to_error_message(
                exception_code) + ")"
        exc = excinfo.value

        #assert (сохраняем оригинальный текст)
        error_message = OperationResponse.code_to_error_message(
            exception_code)  # сохраняем оригинальное имя метода codeToErrorMessage как есть
        assert exc.response is not None, f"Exception responce is null during exceptio({error_message}) on getBalance"
        assert exc.response.code == exception_code, f"Exception code is not relevant to server answer during exceptio({error_message}) on getBalance"

    def test_client_deposit_correct_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        delta_correct_deposit = 100.0

        #record
        BankStub(self.auth_source, self.data_source)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        #act
        ret_balance = client.deposit(a, delta_correct_deposit)

        #assert
        assert ret_balance == delta_correct_deposit, "returned balance after correct deposit not equal to expected one"

    def test_client_deposit_correct_get_balance_test_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        delta_correct_deposit = 100.0

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.data_source.deposit.return_value = OperationResponse(OperationResponse.SUCCEED, delta_correct_deposit)
        self.data_source.get_balance.return_value = OperationResponse(OperationResponse.SUCCEED, delta_correct_deposit)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.deposit(a, delta_correct_deposit)  # act part of deposit

        #act for get balance
        ret_balance = client.get_balance(a)

        #assert
        assert ret_balance == delta_correct_deposit, "getBalance after correct deposit not equal to expected one"

    def test_client_deposit_local_not_logged_exception(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_correct_deposit = 100.0

        #record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)  # perform logout

        #act
        with pytest.raises(OperationException) as excinfo:
            client.deposit(a,
                           delta_correct_deposit), "Exception not thrown for deposit after some server code(" + OperationResponse.code_to_error_message(
                OperationResponse.NOT_LOGGED) + ")"
        exc = excinfo.value

        #assert
        assert exc.response is not None, "Exception responce is null for exception on incorrect deposit"
        assert exc.response.code == OperationResponse.NOT_LOGGED, (
            "Exception code is not relevant to server answer for exception on incorrect deposit")

    def test_client_deposit_not_logged_exception_get_balance(self):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_correct_deposit = 100.0

        # record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        # arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)

        try:
            Client.deposit(a, delta_correct_deposit)
        except OperationException as _:
            pass

        a = client.login(correct_login, correct_password)

        # act
        balance_after = Client.get_balance(a)

        # assert
        assert start_balance == balance_after, "After not logged deposit balance was changed"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR,
    ])
    def test_client_deposit_exceptions(self, exception_code):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        delta_correct_deposit = 100.0

        # record
        BankStub(self.auth_source, self.data_source, deposit_error=exception_code)

        # arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        # act
        with pytest.raises(OperationException) as excinfo:
            Client.deposit(a, delta_correct_deposit), \
                f"Exception not thrown for deposit after some server code({OperationResponse.code_to_error_message(exception_code)})"

        exc = excinfo.value
        # assert
        assert exception_code == exc.response.code, "Exception code is not relevant to server answer"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR,
    ])
    def test_client_deposit_exceptions_get_balance(self, exception_code):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_correct_deposit = 100.0

        # record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance, deposit_error=exception_code)

        # arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)
        try:
            Client.deposit(a, delta_correct_deposit)
        except OperationException as _:
            pass
        a = client.login(correct_login, correct_password)

        # act
        balance_after_deposit = Client.get_balance(a)

        # assert
        assert start_balance == balance_after_deposit, "After unsucceed not logged deposit balance was changed"

    def test_withdraw_no_money(self):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        session_id = 1
        more_balance_withdraw = 100.0
        initial_balance = 50.0

        # record
        BankStub(self.auth_source, self.data_source, initial_balance=initial_balance)


        # arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)

        # act
        with pytest.raises(OperationException) as excinfo:
            Client.withdraw(account, more_balance_withdraw)
        exception = excinfo.value

        # assert
        assert exception.response is not None, "Response is null for no-money call of withdraw"
        assert exception.response.code == OperationResponse.NO_MONEY, "Return code is not NO MONEY for no-money call of withdraw"
        assert exception.response.body == initial_balance, "Response body does not contain initial balance for no-money call of withdraw"

    def test_withdraw_successful(self):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        session_id = 1
        deposit_amount = 500.0
        withdraw_amount = 200.0

        # record
        BankStub(self.auth_source, self.data_source)

        # arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)
        Client.deposit(account, deposit_amount)

        # act
        actual_balance = Client.withdraw(account, withdraw_amount)

        # assert
        assert actual_balance == deposit_amount - withdraw_amount, "Incorrect balance after successful withdraw"

    def test_withdraw_correct_balance_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(
            correct_password)  # Замените на актуальную реализацию получения хеша пароля
        session_id = 1
        start_balance = 0.0
        delta_withdraw = 100.0
        delta_deposit = 100.0

        #record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)
        Client.deposit(account, delta_deposit)
        Client.withdraw(account, delta_withdraw)

        #act
        ret_balance = Client.get_balance(account)

        #assert (сохранён оригинальный assert-текст)
        assert ret_balance == (
                    delta_deposit - delta_withdraw), "getBalance after correct withdraw not equal to expected one"

    def test_withdraw_not_logged_exception(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        delta_withdraw = 100.0

        #record
        BankStub(self.auth_source, self.data_source)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)
        client.logout(account)

        #act
        with pytest.raises(OperationException) as excinfo:
            Client.withdraw(account, delta_withdraw), \
                f"Exception not thrown for withdraw after some server code({OperationResponse.code_to_error_message(OperationResponse.NOT_LOGGED)})"
        exc = excinfo.value

        #assert
        assert exc.response is not None, "Exception responce is null after exception(\"+OperationResponse.codeToErrorMessage(OperationResponse.NOT_LOGGED)+\") for withdraw"
        assert exc.response.code == OperationResponse.NOT_LOGGED, \
            "Exception code is not relevant to server answer after exception(\"+OperationResponse.codeToErrorMessage(OperationResponse.NOT_LOGGED)+\") for withdraw"

    def test_withdraw_not_logged_get_balance(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_withdraw = 100.0

        #record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)
        client.logout(account)
        try:
            Client.withdraw(account, delta_withdraw)
        except OperationException as _:
            pass
        new_account = client.login(correct_login, correct_password)

        #act
        balance_after = Client.get_balance(new_account)

        #assert
        assert balance_after == start_balance, "After not logged withdraw balance was changed"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR,
    ])
    def test_client_withdraw_exceptions(self, exception_code):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_correct_withdraw = 100.0

        # record
        BankStub(self.auth_source, self.data_source, withdraw_error=exception_code)

        # arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        # act
        with pytest.raises(OperationException) as excinfo:
            Client.withdraw(a, delta_correct_withdraw), \
                f"Exception not thrown for deposit after some server code({OperationResponse.code_to_error_message(exception_code)})"
        exc = excinfo.value

        # assert
        assert exc.response is not None, \
            f"Exception response is null for withdraw after server code({OperationResponse.code_to_error_message(exception_code)})"
        assert exc.response.code == exception_code, \
            f"Exception code is not relevant to server answer for withdraw after server code({OperationResponse.code_to_error_message(exception_code)})"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.NOT_LOGGED,
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR
    ])
    def test_client_withdraw_exceptions_get_balance(self, exception_code):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        start_balance = 0.0
        delta_correct_withdraw = 100.0

        # record
        BankStub(self.auth_source, self.data_source, initial_balance=start_balance, withdraw_error=exception_code)

        # Arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)
        try:
            Client.withdraw(a, delta_correct_withdraw)
        except OperationException:
            pass
        a = client.login(correct_login, correct_password)

        # act
        balance_after_withdraw = Client.get_balance(a)

        # assert
        assert balance_after_withdraw == start_balance, \
            "After not logged withdraw the balance was changed"
