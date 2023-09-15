class SecParserError(Exception):
    pass


class SecParserValueError(SecParserError, ValueError):
    pass


class SecParserRuntimeError(SecParserError, RuntimeError):
    pass
