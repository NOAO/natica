class BaseNaticaException(Exception):
    status_code = None
    error_message = None
    is_an_error_response = True

    def __init__(self, error_message):
        Exception.__init__(self)
        self.error_message = error_message
        
    def to_dict(self):
        return {'errorMessage': self.error_message}

class InvalidUsage(BaseNaticaException):
    status_code = 400


class UnknownSearchField(BaseNaticaException):
    status_code = 400
    

class BadTIFormat(BaseNaticaException):
    status_code = 400    

class BadNumeric(BaseNaticaException):
    status_code = 400    

class BadSearchSyntax(BaseNaticaException):
    status_code = 400    

class BadFakeError(BaseNaticaException):
    status_code = 400    

class CannotProcessContentType(BaseNaticaException):
    status_code = 400
    
    
class CannotStoreInDB(BaseNaticaException):
    status_code = 400
