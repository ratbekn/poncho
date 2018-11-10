from .poncho_base_exception import PonchoException


class ArgParserError(PonchoException):
    pass


class NoArgumentsError(ArgParserError):
    pass
