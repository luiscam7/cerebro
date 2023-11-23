import pytest
from flask import url_for
from flask_testing import TestCase

from src.application import app


class TestHelloWorld(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_hello_world(self):
        response = self.client.get(url_for("hello_world"))
        assert response.status_code == 200
        assert b"Hello, World!" in response.data


if __name__ == "__main__":
    pytest.main()
