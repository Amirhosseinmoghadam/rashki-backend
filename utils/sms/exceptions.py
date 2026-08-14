class SMSException(Exception):
    """Base exception for SMS utilities."""


class SMSConfigurationError(SMSException):
    """SMS configuration is missing or invalid."""


class SMSConnectionError(SMSException):
    """Could not connect to the SMS provider."""


class SMSProviderError(SMSException):
    """SMS provider returned an error."""


class SMSValidationError(SMSException):
    """Invalid SMS input."""