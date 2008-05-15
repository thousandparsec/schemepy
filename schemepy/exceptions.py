# Exception hierarchy for Schemepy

class Error(Exception):
    "The base class for the Exceptions in Schemepy."
    def __str__(self):
        return self.message


class ConversionError(Error):
    """\
    Exception raised if a conversion can't be done properly.

    Attributes:
        value   - the value to be converted
        message - the error message
    """
    
    def __init__(self, value, message):
        self.value = value
        self.message = message
        
    
class VMNotFoundError(Error):
    """\
    Exception raised when no VM can be found.
    Attributes:
        message - the error message
    """
    
    def __init__(self, message):
        self.message = message

class ProfileNotFoundError(Error):
    """\
    Exception raised when no profile can be found.
    Attributes:
        message - the error message
    """
    def __init__(self, message):
        self.message = message

class BackendNotFoundError(Error):
    """\
    Exception raised when no backend can be found.
    Attributes:
        message - the error message
    """

    def __init__(self, message):
        self.message = message

class SchemeError(Error):
    """\
    Common ancestor of all exceptions raised by Scheme code.
    Attributes:
        message - the error message
    """
    def __init__(self, message):
        self.message = message

class ScmSystemError(SchemeError):
    """\
    Exception raised when receiving an unhandled fatal signal
    such as SIGSEGV, SIGBUS, SIGFPE etc. or when the operating
    system indicates an error condition.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmNumericalError(SchemeError):
    """\
    Exception raised when there's a numerical overflow.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmRangeError(SchemeError):
    """\
    Exception raised when the arguments to a procedure do not fall
    within the accepted domain.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmWrongArgType(SchemeError):
    """\
    Exception raised when an argument to a procedure has the wrong
    type.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmWrongArgNumber(SchemeError):
    """\
    Exception raised when a procedure was called with the wrong
    number of arguments.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmSyntaxError(SchemeError):
    """\
    Exception raised when there's an syntax error in the Scheme code.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmUnboundVariable(SchemeError):
    """\
    Exception raised when trying to access an unbound variable.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

class ScmMiscError(SchemeError):
    """\
    Other errors.
    """
    def __init__(self, message):
        SchemeError.__init__(self, message)

