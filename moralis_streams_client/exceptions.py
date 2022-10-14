# streams api exceptions


class MoralisStreamsError(Exception):
    pass


class MoralisStreamsErrorReturned(MoralisStreamsError):
    pass


class MoralisStreamsCallFailed(MoralisStreamsError):
    pass


class MoralisStreamsResponseFormatError(MoralisStreamsError):
    pass
