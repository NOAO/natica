import logging
import traceback

class BaseNaticaException(Exception):
    status_code = None
    error_message = None
    is_an_error_response = True

    def __init__(self, error_message):
        Exception.__init__(self)
        self.error_message = error_message
        logging.error('BaseNaticaException: {}; {}'
                      .format(error_message, traceback.format_stack()))
        
    def to_dict(self):
        return {'errorMessage': self.error_message}

class UsageError(BaseNaticaException):
    status_code = 400

class ExtraSearchFieldError(BaseNaticaException):
    status_code = 400

class TIFormatError(BaseNaticaException):
    status_code = 400    

class NumericError(BaseNaticaException):
    status_code = 400    

class SearchSyntaxError(BaseNaticaException):
    status_code = 400    

class BadFakeError(BaseNaticaException):
    status_code = 400    

class ContentTypeError(BaseNaticaException):
    status_code = 400
    
    
class DBStoreError(BaseNaticaException):
    status_code = 400

class IngestError(BaseNaticaException):
    status_code = 400

class MissingFieldError(BaseNaticaException):
    status_code = 400

class ConflictingValuesError(BaseNaticaException):
    status_code = 400

class TelescopeError(BaseNaticaException):
    status_code = 400

class InstrumentError(BaseNaticaException):
    status_code = 400

class FitsError(BaseNaticaException):
    status_code = 400
    
    
class PropNotFound(BaseNaticaException):
    status_code = 400



    
