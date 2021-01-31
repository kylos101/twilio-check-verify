# twilio-check-verify

A function to check verification codes using [Twilio's Verify API](https://www.twilio.com/docs/verify/api) with [OpenFaaS](https://www.openfaas.com/).

Refer to [twilio-send-verify](https://github.com/kylos101/twilio-send-verify) to send verification codes.

## Overview

This function requests Twilio to check a Verification Code for validity.

The response looks like this:

```json
{
  "channel": "sms",
  "date_created": "Sun, 31 Jan 2021 16:25:51 GMT",
  "date_updated": "Sun, 31 Jan 2021 16:26:25 GMT",
  "status": "approved",
  "to": "+15551234567",
  "valid": true
}
```

### Checking Codes More Than Once

A request to check the same verification code two or more times will result in a 500 error from this API, and a 404 error from Twilio, which is logged in the error.

## A Sample Use Case

Let's pretend you have another function written in Python that does user profile updates, and it handles the following scenario.

Given a user wants to opt into receive notifications via SMS, and received a verification code, and has sent a verification code to us, when the verification code is sent to Twilio and a valid response is returned, then the user's profile must be updated accordingly.

Sending a request to `twilio-check-verify` to ask Twilio to check the verification code may look like:

```python
url = "http://gateway.openfaas.svc.cluster.local:8080/function/twilio-check-verify.openfaas-fn"
body = {"To": "15551234567", "Code": "123456"}
response = requests.post(url, json=body)
response.raise_for_status()
```

This will result in the API receiving [a response like this one](##Overview).

## Installation

1. Create a Verify service in [Twilio console](https://www.twilio.com/console/verify/services). Document the `Service ID`, you'll need it in step 4.

2. Save the `AccountSid` and `AuthToken` from Twilio as a secret in Kubernetes

```bash
# get these from https://www.twilio.com/console
TWILIO_ACCOUNT_SID=<YOUR_ACCOUNT_SID>
TWILIO_AUTH_TOKEN=<YOUR_AUTH_TOKEN>
faas-cli secret create twilio-account-sid --from-literal=$TWILIO_ACCOUNT_SID
faas-cli secret create twilio-auth-token --from-literal=$TWILIO_AUTH_TOKEN
```

3. Make sure you have the `python3-http` template on your machine

```bash
faas-cli template store pull python3-http
```

4. Configue it to your liking and ship it to OpenFaaS

```yaml
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:8080
functions:
  twilio-check-verify:
    lang: python3-http
    handler: ./twilio_check_verify
    secrets:
      - twilio-account-sid
      - twilio-auth-token
    labels:
      com.openfaas.scale.zero: false
    environment:
      twilio_check_verify_endpoint: https://verify.twilio.com/v2/Services/<YOUR_VERIFY_SERVICE_ID>/VerificationCheck
      twilio_account_sid_path: /var/openfaas/secrets/twilio-account-sid
      twilio_auth_token_path: /var/openfaas/secrets/twilio-auth-token
```
