# Exception hierarchy for Schemepy

class Error(Exception):
    "The base class for the Exceptions in Schemepy."
    pass


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
