from pydantic import BaseModel


class TwilioCheckVerifyCommand(BaseModel):
    """ Check a verification code with Twilio """
    # There are other inputs we could use, these two are required
    To: str
    Code: str

    def to_dict(self) -> dict:
        include_keys = {
            "To", "Code"
        }
        return self.dict(include=include_keys)
