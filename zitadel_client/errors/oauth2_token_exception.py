from zitadel_client.errors import ZitadelException


class OAuth2TokenException(ZitadelException):
    """Exception for an OAuth2 token endpoint that answered 2xx with a body the
    SDK cannot use: not a JSON object, or without a non-empty ``access_token``.
    """
