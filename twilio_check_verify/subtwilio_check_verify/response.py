from pydantic import BaseModel
from datetime import datetime


class TwilioCheckVerifyResponse(BaseModel):
    """ A check verify respons from Twilio """
    # The API returns other fields, but, these are the ones that are most helpful
    to: str
    channel: str
    status: str
    valid: bool
    date_created: datetime
    date_updated: datetime

    def to_dict(self) -> dict:
        include_keys = {
            "to", "channel", "status", "valid", "date_created", "date_updated"
        }
        return self.dict(include=include_keys)
