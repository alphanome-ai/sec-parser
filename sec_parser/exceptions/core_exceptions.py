class SecParserError(Exception):
    """
    Base exception class for sec_parser.
    All custom exceptions in sec_parser are inherited from this class.
    """


class SecParserValueError(SecParserError, ValueError):
    pass


class SecParserRuntimeError(SecParserError, RuntimeError):
    pass
