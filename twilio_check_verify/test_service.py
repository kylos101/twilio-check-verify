import unittest
from unittest.mock import patch, mock_open
from .subtwilio_check_verify import TwilioCheckVerifyService
import base64
import os
import urllib.parse
from pydantic import ValidationError


class TwilioCheckVerifyServiceTests(unittest.TestCase):
    def setUp(self):
        self.twilio_account_sid_path = "/var/openfaas/secrets/twilio-account-sid"
        self.twilio_auth_token_path = "/var/openfaas/secrets/twilio-auth-token"
        self.twilio_check_verify_endpoint = "https://verify.twilio.com/v2/Services/foo/VerificationCheck"
        os.environ["twilio_account_sid_path"] = self.twilio_account_sid_path
        os.environ["twilio_auth_token_path"] = self.twilio_auth_token_path
        os.environ["twilio_check_verify_endpoint"] = self.twilio_check_verify_endpoint
        self.service = TwilioCheckVerifyService()
        self.mock_secret = {
            self.twilio_account_sid_path: "sid",
            self.twilio_auth_token_path: "token"
        }

    def test_can_construct_service(self):
        assert self.service is not None
        assert self.service.settings.twilio_auth_token_path == self.twilio_auth_token_path
        assert self.service.settings.twilio_account_sid_path == self.twilio_account_sid_path
        assert self.service.settings.twilio_check_verify_endpoint == self.twilio_check_verify_endpoint

    def test_get_secret_can_read(self):
        self.mock_sid = "sid\n"
        with patch('builtins.open', mock_open(read_data=self.mock_sid)):
            result = self.service.get_secret(self.twilio_account_sid_path)
            assert result is not None
            assert "sid" == result

    def test_get_command_returns(self):
        cmd = self.service.get_command({"To": "15551234567", "Code": "123456"})
        assert cmd["To"] == "15551234567"
        assert cmd["Code"] == "123456"

    def test_get_command_invalid_body_throws(self):
        """ ValidationError will cause the API to return HTTP 400 """
        with self.assertRaises(ValidationError):
            self.service.get_command({})
        with self.assertRaises(ValidationError):
            self.service.get_command({"To": "no code"})
        with self.assertRaises(ValidationError):
            self.service.get_command({"Code": "0"})

    # don't try to read secrets from a file when testing get_headers()
    def mock_get_secret(self, path) -> str:
        return self.mock_secret[path]

    def test_get_headers_returns(self):
        self.service.get_secret = self.mock_get_secret
        expected_header_bytes = "sid:token".encode("utf-8")
        expected_authorization_header = "Basic " + base64.b64encode(
            expected_header_bytes).decode("utf-8")
        actual_header = self.service.get_headers()
        assert expected_authorization_header == actual_header["authorization"]

    def test_get_request_body_returns_with_phone(self):
        input = {
            "To": "18605551234",
            "Code": "123456"
        }
        expected = {
            "To": "+18605551234",
            "Code": "123456"
        }
        expected_output = urllib.parse.urlencode(expected)
        actual_output = self.service.get_request_body(input)
        assert expected_output == actual_output

    def test_get_request_body_returns_with_email(self):
        input = {
            "To": "foo@bar.com",
            "Code": "123456"
        }
        expected = {
            "To": "foo@bar.com",
            "Code": "123456"
        }
        expected_output = urllib.parse.urlencode(expected)
        actual_output = self.service.get_request_body(input)
        assert expected_output == actual_output
