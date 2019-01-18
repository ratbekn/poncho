from .poncho_base_exception import PonchoException  # pragma: no cover


class ArgParserError(PonchoException):  # pragma: no cover
    pass


class NoArgumentsError(ArgParserError):  # pragma: no cover
    pass
