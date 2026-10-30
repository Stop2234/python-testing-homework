
import pytest
from unittest import mock

from ru.hse.OperationException import OperationException
from ru.hse.Account import Account
from ru.hse.OperationResponse import OperationResponse
from ru.hse.client.AccountManager import AccountManager
from ru.hse.client.Client import Client
from ru.hse.IAuthorizationSource import IAuthorizationSource
from ru.hse.IAccountDataSource import IAccountDataSource

class TestServerlessClientIntegrationAuth:
    def setup_method(self):
        self.data_source = mock.create_autospec(IAccountDataSource)
        self.auth_source = mock.create_autospec(IAuthorizationSource)


    def test_client_login_correct_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)

        #arrange_2
        client = Client(self.auth_source, self.data_source)

        #act
        account = client.login(correct_login, correct_password)

        #assert
        assert account is not None, "Account is null after succeed login"
        assert account.active_session == session_id, "Active session incorrect after correct login"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.NO_USER_INCORRECT_PASSWORD,
        OperationResponse.ALREADY_LOGGED
    ])
    def test_client_login_exceptions(self, exception_code):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(exception_code, session_id if exception_code == OperationResponse.ALREADY_LOGGED else None)

        #arrange_2
        client = Client(self.auth_source, self.data_source)

        #act
        with pytest.raises(OperationException) as excinfo:
            client.login(correct_login, correct_password)#, f"Exception not thrown after some server code({OperationResponse.code_to_error_message(exception_code)})"

        #assert
        assert excinfo.value.response.code == exception_code, "Exception code is not relevant to server answer"

    def test_client_logout_login_correct_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.SUCCEED)


        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)
        client.logout(a)

        #act
        a = client.login(correct_login, correct_password)

        #assert
        assert a is not None, "Login - logout - login sequence needs to be succeed but it is not"

    def test_client_login_login_already_logged(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        client.login(correct_login, correct_password)

        #act
        with pytest.raises(OperationException) as excinfo:
            client.login(correct_login, correct_password), "Exception not thrown for login after some server code(" + OperationResponse.code_to_error_message(OperationResponse.ALREADY_LOGGED) + ")"

        #assert
        exc = excinfo.value
        assert exc.response.code == OperationResponse.ALREADY_LOGGED, "Logout failed after succeed local login"

    # clientLogoutNotLoggedRemote
    def test_client_logout_not_logged_remote(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.NOT_LOGGED)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        #act
        with pytest.raises(OperationException) as excinfo:
            client.logout(a)

        exc = excinfo.value

        #assert
        assert exc is not None, "server returned not logged logout is not resulted by non-empty exeption"
        assert exc.response is not None, "server returned not logged logout causes null response"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "server returned not logged logout causes non NOT LOGGER return code"

    def test_client_logout_not_logged_local(self):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1
        client = Client(self.auth_source, self.data_source)
        a = Account(correct_login)  # white box :(
        a.activeSession = session_id
        a.init_data_storage(self.data_source)

        # act
        with pytest.raises(OperationException) as exc_info:
            client.logout(a)

        # assert
        exc = exc_info.value
        assert exc is not None, "not logged logout is not resulted by non-empty exeption"
        assert exc.response is not None, "not logged logout causes null response"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "not logged logout causes non NOT LOGGER return code"

    def test_client_logout_logged_success(self):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.SUCCEED)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        # act
        result = client.logout(a)

        # assert
        assert result is True, "Logout not succeed but it tends to be so"

    @pytest.mark.parametrize("exception_code", [
        OperationResponse.CONNECTION_ERROR,
        OperationResponse.UNDEFINED_ERROR,
    ])
    def test_client_logout_exceptions(self, exception_code):
        # arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)
        session_id = 1

        # record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.auth_source.logout.return_value = OperationResponse(exception_code)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        a = client.login(correct_login, correct_password)

        # act
        with pytest.raises(OperationException) as exc_info:
            client.logout(a), f"Exception not thrown for logout after some server code({OperationResponse.code_to_error_message(exception_code)})"

        # assert
        exc = exc_info.value
        assert exc.response is not None, "Exception responce object is null after incorrect login"
        assert exc.response.code == exception_code, "Exception code is not relevant to server answer"

    def test_client_double_logout_logged_success(self):
        #arrange
        correct_login = "someLogin"
        correct_password = "somePassword"
        encoded_password = AccountManager.get_encoded_password(correct_password)  # Предположим, что метод get_encoded_password имитирован или существует в классе (используется как есть)
        session_id = 1

        #record
        self.auth_source.login.return_value = OperationResponse(OperationResponse.SUCCEED, session_id)
        self.auth_source.logout.return_value = OperationResponse(OperationResponse.SUCCEED)

        #arrange_2
        client = Client(self.auth_source, self.data_source)
        account = client.login(correct_login, correct_password)
        client.logout(account)

        #act
        with pytest.raises(OperationException) as exc_info:
            client.logout(account)

        exc = exc_info.value

        #assert
        assert exc is not None, "second attempt logout is not resulted by non-empty exeption"
        assert exc.response is not None, "second attempt logout causes null response"
        assert exc.response.code == OperationResponse.NOT_LOGGED, "second attempt logout causes non NOT LOGGER return code"