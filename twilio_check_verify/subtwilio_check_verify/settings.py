from pydantic import BaseSettings


class TwilioCheckVerifySettings(BaseSettings):
    """ Settings to work with our User Service """
    twilio_check_verify_endpoint: str
    twilio_auth_token_path: str
    twilio_account_sid_path: str
