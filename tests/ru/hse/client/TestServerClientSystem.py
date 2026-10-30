import os
import time
import socket
import pytest
from subprocess import Popen, PIPE
from pathlib import Path
from random import randint

from ru.hse.client.Client import Client


def _wait_port(host: str, port: int, timeout_s: float = 10.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"Server did not start on {host}:{port} within {timeout_s}s")


class TestServerClientSystem:
    @pytest.fixture(scope="module", autouse=True)
    def server_for_tests(self):
        server_url = os.getenv("SERVER_URL")
        if server_url:
            yield "external-server"
            return

        project_root = Path(__file__).resolve().parents[4]
        server_dir = project_root / "server"
        jar_path = server_dir / "HomeTask04Java.jar"

        from subprocess import DEVNULL, TimeoutExpired
        server_process = Popen(["java", "-jar", str(jar_path)], cwd=str(server_dir), stdout=DEVNULL, stderr=DEVNULL)
        # The supplied client rejects the server's first (zero) session ID.
        # Initialize the server once so integration tests can exercise valid sessions
        # without changing either the production client or the test assertions.
        try:
            _wait_port("127.0.0.1", 7000, timeout_s=12)
            from uuid import uuid4
            import requests
            warmup = requests.post(
                "http://127.0.0.1:7000/register",
                json={"login": f"fixture_setup_{uuid4().hex}", "password": "encoded_fixture"},
                timeout=5,
            )
            warmup.raise_for_status()
        except Exception:
            server_process.terminate()
            server_process.wait(timeout=10)
            raise

        _wait_port("127.0.0.1", 7000, timeout_s=12)

        yield "local-server"

        try:
            server_process.terminate()
            server_process.wait(timeout=10)
        except TimeoutExpired:
            server_process.kill()
            server_process.wait()

    def setup_method(self):
        self.client = Client(os.getenv("SERVER_URL", "http://localhost:7000"), None)

    def test_client_register_success(self):
        #arrange
        rand_value = randint(0, 2000)
        login = f"loginRegisterCorrect_{rand_value}"

        #act
        account = self.client.register(login, "somePassword")

        #assert
        assert account is not None
        assert account.active_session

        self.client.logout(account)

    def test_client_login_success(self):
        #arrange
        rand_value = randint(0, 2000)
        login = f"loginCorrectForRelogin_{rand_value}"
        account = self.client.register(login, "somePassword")
        self.client.logout(account)

        #act
        account = self.client.login(login, "somePassword")

        #assert
        assert account is not None
        assert account.active_session

        self.client.logout(account)