from .subtwilio_check_verify import TwilioCheckVerifyService

s = TwilioCheckVerifyService()


def handle(event, context):
    return s.handle(event)
