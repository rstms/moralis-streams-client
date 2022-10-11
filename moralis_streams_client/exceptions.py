# streams api exceptions


class MoralisStreamsError(Exception):
    pass


class ErrorReturned(MoralisStreamsError):
    pass


class CallFailed(MoralisStreamsError):
    pass


class ResponseFormatError(MoralisStreamsError):
    pass
