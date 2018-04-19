import requests
import json

itop_error_codes = {
    0: 'OK - No issue has been encountered',
    1: "UNAUTHORIZED - Missing/wrong credentials or the user does not have enough rights to perform the requested " +
       "operation",
    2: "MISSING_VERSION - The parameter 'version' is missing",
    3: "MISSING_JSON - The parameter 'json_data' is missing",
    4: 'INVALID_JSON - The input structure is not valid JSON string',
    5: "MISSING_AUTH_USER - The parameter 'auth_user' is missing",
    6: "MISSING_AUTH_PWD - The parameter 'auth_pwd' is missing",
    10: "UNSUPPORTED_VERSION - No operation is available for the specified version",
    11: "UNKNOWN_OPERATION - The requested operation is not valid for the specelified version",
    12: "UNSAFE - The requested operation cannot be performe because it can cause data (integrity) loss",
    100: "INTERNAL_ERROR - The operation could not be performed, see the message for troubleshooting"
}


class ItopError(requests.exceptions.ConnectionError):
    def __init__(self, *args, **kwargs):
        """Initialize ItopError with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request

        json_return = json.loads(response.content.decode('utf-8'))
        return_code = json_return['code']
        message = json_return['message']

        if return_code in itop_error_codes:
            itop_error = "%s %s." % (return_code, itop_error_codes[return_code])
        else:
            itop_error = "UNKNOW_ERROR - Not specified by ITOP."

        super(ItopError, self).__init__(message + "\n" + itop_error)