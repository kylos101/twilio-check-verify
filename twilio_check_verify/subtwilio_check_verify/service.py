import json
import base64
import urllib.parse
import requests
from pydantic import ValidationError
import traceback
from .settings import TwilioCheckVerifySettings
from .command import TwilioCheckVerifyCommand
from .response import TwilioCheckVerifyResponse
import logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class TwilioCheckVerifyService():
    def __init__(self):
        self.settings = TwilioCheckVerifySettings()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("__init__")

    def handle(self, event):
        self.log("handle")
        response: dict

        try:
            body = json.loads(event.body)

            # build an object representing acceptable input
            verify_cmd = self.get_command(body)

            # setup our request body
            request = self.get_request_body(verify_cmd)

            # setup our auth header
            headers = self.get_headers()

            # ask Twilio if it is valid
            url = self.settings.twilio_check_verify_endpoint
            verify_response = requests.post(
                url, data=request, headers=headers)
            verify_response.raise_for_status()

            # build an object representing acceptable output and return it
            v: dict = verify_response.json()
            t = TwilioCheckVerifyResponse.parse_obj(v)
            response = {
                "status": 200,
                "body": t.to_dict()
            }

        except ValidationError:
            msg = traceback.format_exc()
            self.log(msg)

            response = {
                "statusCode": 400,
                "body": "Bad Request"
            }
        except ValueError:
            msg = traceback.format_exc()
            self.log(msg)
            response = {
                "statusCode": 400,
                "body": "Bad Request"
            }
        except Exception:
            msg = traceback.format_exc()
            self.log(msg)
            response = {
                "statusCode": 500,
                "body": "Internal Server Error"
            }
        finally:
            return response

    def log(self, msg: str):
        self.logger.error(__name__ + ":" + str(msg))

    def get_secret(self, path: str) -> str:
        """Get a secret from a file."""
        location = path
        with open(location, "r") as fo:
            line = fo.readline().strip()
        return line

    def get_request_body(self, command: TwilioCheckVerifyCommand) -> str:
        """Build and return a url encoded post body."""
        self.log("get_request_bytes")
        to: str
        if command["To"].isnumeric():
            # its a phone #
            to = f'+{command["To"]}'
        else:
            # its an email, probably.
            to = f'{command["To"]}'
        request_dict = {
            "To": to,
            "Code": command["Code"]
        }
        ret_val = urllib.parse.urlencode(request_dict)
        return ret_val

    def get_headers(self) -> dict:
        """Get the headers needed to call the Verify Check endpoint."""
        self.log("get_headers")
        sid = self.get_secret(self.settings.twilio_account_sid_path)
        token = self.get_secret(self.settings.twilio_auth_token_path)

        auth_header_bytes = f'{sid}:{token}'.encode("utf-8")
        b64_auth_header = base64.b64encode(auth_header_bytes).decode("utf-8")

        return {
            'authorization': 'Basic ' + b64_auth_header,
            'content-type': 'application/x-www-form-urlencoded'
        }

    def get_command(self, body: dict) -> dict:
        """Return a dict of acceptable inputs by reading in the body.
        Will throw ValidationError if cannot parse required fields """
        return TwilioCheckVerifyCommand.parse_obj(body).to_dict()
