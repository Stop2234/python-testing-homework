import pytest
from unittest import mock

from ru.hse.OperationException import OperationException
from ru.hse.Account import Account
from ru.hse.client.AccountManager import AccountManager
from ru.hse.IAccountDataSource import IAccountDataSource
from ru.hse.IAuthorizationSource import IAuthorizationSource
from ru.hse.OperationResponse import OperationResponse


class TestServerlessAccountManagerAuth:
    def setup_method(self):
        self.data_source = mock.create_autospec(IAccountDataSource)
        self.auth_source = mock.create_autospec(IAuthorizationSource)

    def test_login_success(self):
        #arrange
        correct_login = "user"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(
            correct_password)  # Предположим, что метод существует в классе или импортирован
        correct_session = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)

        #arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)

        #act
        account = account_manager.login(correct_login, correct_password)

        #assert
        assert account is not None, "Account is null after succeed login"
        assert account.active_session == correct_session, "Account session is incorrect"
        assert len(account_manager.get_exceptions()) == 0, "Exceptions should be empty after successful login"

    def test_call_login_invalid_credentials(self):
        #arrange
        correct_login = "user"
        incorrect_password = "wrongPassword"  # Исправлено: должно отличаться от корректного пароля в коде Java (в оригинале оба были somePassword)
        encodedIncorrect = AccountManager.get_encoded_password(incorrect_password) if hasattr(AccountManager,
                                                                                              'get_encoded_password') else ""

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.NO_USER_INCORRECT_PASSWORD)

        #arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)

        #act
        account = account_manager.login(correct_login, incorrect_password)
        exceptions = account_manager.get_exceptions()

        if exceptions:
            exc = exceptions[0]
        else:
            exc = None

        #assert
        assert account is None, "Account is not null after login with invalid credentials"
        assert len(exceptions) == 1, "AccountManager contains 0 or >1 exceptions after incorrect credentials login"

        if exc and isinstance(exc, OperationException):
            response = exc.response
            assert response.code == OperationResponse.NO_USER_INCORRECT_PASSWORD, "Response code is not INCORRECT CREDENTIALS after incorrect credentials call for login"
            assert response.body is None, "Response body is not null after incorrect credentials call of login"
        else:
            raise AssertionError("Response is null after incorrect credentials call of login")

    def test_call_login_already_logged_remote(self):
        #arrange
        correct_login = "user"
        incorrect_password = "somePassword"
        encodedIncorrect = "mocked_encoded"
        correct_session = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.ALREADY_LOGGED, correct_session)

        #arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)

        #act
        account = account_manager.login(correct_login, incorrect_password)
        exceptions = account_manager.get_exceptions()
        exc = exceptions[0] if exceptions else None

        # Asserts
        assert account is None, "Account не должен быть создан при уже существующей авторизации"
        assert len(exceptions) == 1, "Количество ошибок должно быть ровно 1"
        assert isinstance(exc, OperationException), "Исключение должно быть типа OperationException"
        assert exc.response.body == correct_session, f"Session_id в ответе отличается от {correct_session}"
        assert exc.response.code == OperationResponse.ALREADY_LOGGED, "Неверный код ошибки ALREADY_LOGGED"

    def test_call_login_already_logged_local(self):
        #arrange
        correct_login = "user"
        incorrect_password = "somePassword"
        encodedIncorrect = "mocked_encoded"
        correct_session = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)

        #arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)
        account_manager.login(correct_login, incorrect_password)

        #act
        account = account_manager.login(correct_login, incorrect_password)
        exceptions = account_manager.get_exceptions()
        exc = exceptions[-1] if exceptions else None  # Последний exception после повторного вызова login

        # Asserts аналогичны предыдущему тесту с поправкой на локальный кеш:
        assert account is None, "Account is not null after already logged state from local cache for login"
        assert len(
            exceptions) == 1, "AccountManager contains 0 or >1 errors after already logged state from local cache for login"
        assert isinstance(exc,
                          OperationException), "Response is null after already logged state from local cache for login"
        assert exc.response.body == correct_session, "Response body is equal to already logged session after already logged state from local cache for login"
        assert exc.response.code == OperationResponse.ALREADY_LOGGED, "Response code is not ALREADY LOGGED after already logged state from local cache for login"


    #here
    def test_logout_success(self):
        # arrange
        correct_login = "user"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        correct_session = 1

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.SUCCEED)

        # arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)
        account = account_manager.login(correct_login, correct_password)

        # act
        logout_result = account_manager.logout(account)

        # assert
        assert logout_result is True, "False returned after succeed call of logout on correct state and credentials"
        assert len(
            account_manager.get_exceptions()) == 0, "Exceptions happens during succeed call of logout on correct state and credentials"


    def test_logout_not_logged_remote(self):
        # arrange
        correct_login = "user"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        correct_session = 1

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.NOT_LOGGED)

        # arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)
        account = account_manager.login(correct_login, correct_password)

        # act
        logout_result = account_manager.logout(account)
        exc = account_manager.get_exceptions()[0]

        # assert
        assert logout_result is False, "Logout result is true for not_logged code from remote server during logout"
        assert len(
            account_manager.get_exceptions()) == 1, "There are 0 or >1 exceptions for not_logged code from remote server during logout"
        assert exc.response is not None, "Response is null for not_logged code from remote server during logout"
        assert exc.response.body is None, "Response body is null for NOT LOGGED not_logged code from remote server during logout"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "Response code is not NOT LOGGED not_logged code from remote server during logout"


    def test_logout_not_logged_local(self):
        # arrange
        correct_login = "user"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        correct_session = 1

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.SUCCEED)

        # arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)
        account = account_manager.login(correct_login, correct_password)
        account_manager.logout(account)  # First logout call

        # act
        logout_result = account_manager.logout(account)  # Second logout attempt
        exc = account_manager.get_exceptions()[0]

        # assert
        assert logout_result is False, "Logout result is true for logout call with no account in cache"
        assert len(
            account_manager.get_exceptions()) == 1, "There are 0 or >1 exceptions for logout call with no account in cache"
        assert exc.response is not None, "Response is null for logout call with no account in cache"
        assert exc.response.body is None, "Response body is not null for logout call with no account in cache"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "Response code is not NOT LOGGED for logout call with no account in cache"


    def test_account_manager_init_null_argument_first(self):
        # arrange
        manager = None
        data_source = "some_data_source"  # Предполагаем, что dataSource передается как параметр в Java-версии

        # act
        with pytest.raises(OperationException) as excinfo:
            AccountManager(None, self.data_source)

        exc = excinfo.value
        assert exc is not None, "Exception is null after account manager init with first null argument"
        assert exc.response is not None, "Exception response is null after account manager init with first null argument"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, \
            "Exception response code is not NULL ARGUMENT after account manager init with first null argument"
        assert exc.response.body is None, \
            "Exception response body is not null after account manager init with first null argument"


    def test_account_manager_init_null_argument_second(self):
        # arrange
        # act
        with pytest.raises(OperationException) as excinfo:
            AccountManager(self.auth_source, None)

        exc = excinfo.value
        assert exc is not None, "Exception is null after account manager init with second null argument"
        assert exc.response is not None, "Exception response is null after account manager init with second null argument"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, \
            "Exception response code is not NULL ARGUMENT after account manager init with second null argument"
        assert exc.response.body is None, \
            "Exception response body is not null after account manager init with second null argument"


    def test_account_manager_init_null_argument_both(self):
        # arrange
        # act
        with pytest.raises(OperationException) as excinfo:
            AccountManager(None, None)

        exc = excinfo.value
        assert exc is not None, "Exception is null after account manager init with both null arguments"
        assert exc.response is not None, "Exception response is null after account manager init with both null arguments"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, \
            "Exception response code is not NULL ARGUMENT after account manager init with both null arguments"
        assert exc.response.body is None, \
            "Exception response body is not null after account manager init with both null arguments"


    # Тесты для login с null аргументами
    def test_login_null_argument_first(self):
        # arrange
        account_manager = AccountManager(self.auth_source, self.data_source)

        # act
        account = account_manager.login(None, "password")
        exceptions = account_manager.get_exceptions()  # Предполагаем метод get_exceptions() вместо Java-коллекции
        exc = exceptions[0] if exceptions else None

        # Assert
        assert account is None, "Account is not null after login call with first null argument"
        assert len(exceptions) == 1, \
            "There are 0 or >1 exceptions after login call with first null argument"
        assert exc.response is not None, \
            "Exception response is null after login call with first null argument"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, \
            "Exception response code is not NULL ARGUMENT after login call with first null argument"
        assert exc.response.body is None, \
            "Exception response body is not null after login call with first null argument"


    def test_login_null_argument_second(self):
        # arrange
        account_manager = AccountManager(self.auth_source, self.data_source)

        # act
        account = account_manager.login("user1", None)
        exceptions = account_manager.get_exceptions()
        exc = exceptions[0] if exceptions else None

        # assert
        assert account is None, "Account is not null after login call with second null argument"
        assert len(exceptions) == 1, "There are 0 or >1 exceptions after login call with second null argument"
        assert exc.response is not None, "Exception response is null after login call with second null argument"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, "Exception response code is not NULL ARGUMENT after login call with second null argument"
        assert exc.response.body is None, "Exception response body is not null after login call with second null argument"


    def test_logout_null_account(self):
        # arrange
        account_manager = AccountManager(self.auth_source, self.data_source)

        # act
        logout_result = account_manager.logout(None)
        exceptions = account_manager.get_exceptions()
        exc = exceptions[0] if exceptions else None

        # assert
        assert not logout_result, "Logout result is true after logout call with null argument"
        assert len(exceptions) == 1, "There are 0 or >1 exceptions after logout call with null argument"
        assert exc.response is not None, "Exception response is null after logout call with null argument"
        assert exc.response.code == OperationResponse.NULL_ARGUMENT, "Exception response code is not NULL ARGUMENT after logout call with null argument"
        assert exc.response.body is None, "Exception response body is not null after logout call with null argument"


    def test_logout_incorrect_session(self):
        # arrange
        correct_login = "user"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        correct_session = 1
        incorrect_session = 9
        delta_correct_deposit = 100.0

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, correct_session)
        self.auth_source.logout.side_effect = lambda login, session: OperationResponse(OperationResponse.INCORRECT_SESSION if session != correct_session else OperationResponse.SUCCEED)

        # arrange_2
        account_manager = AccountManager(self.auth_source, self.data_source)
        account = account_manager.login(correct_login, correct_password)
        account.active_session = incorrect_session  # assuming activeSession is named as active_session in Python

        # act
        logout_result = account_manager.logout(account)
        exceptions = account_manager.get_exceptions()
        exc = exceptions[0] if exceptions else None

        # assert
        assert not logout_result, "logout result is true for logout call with server answer INCORRECT SESSION"
        assert len(exceptions) == 1, "There are 0 or >1 exceptions for logout call with server answer INCORRECT SESSION"
        assert exc.response is not None, "Exception response is null for logout call with server answer INCORRECT SESSION"
        assert exc.response.code == OperationResponse.INCORRECT_SESSION, "Exception response code is not INCORRECT SESSION for logout call with server answer INCORRECT SESSION"
        assert exc.response.body is None, "Exception response body is not null for logout call with server answer INCORRECT SESSION"
