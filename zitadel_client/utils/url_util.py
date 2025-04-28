class URLUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_hostname(host: str) -> str:
        """
        Processes the host string. This might include cleaning up the input,
        adding a protocol, or other logic similar to your Java URLUtil.buildHostname method.
        """
        # For example, trim whitespace and ensure the host starts with 'https://'
        host = host.strip()
        # noinspection HttpUrlsUsage
        if not host.startswith("http://") and not host.startswith("https://"):
            host = "https://" + host
        return host
