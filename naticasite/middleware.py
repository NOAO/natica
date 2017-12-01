import traceback
from django.http import JsonResponse

def is_registered(exception):
    try:
        return exception.is_an_error_response
    except AttributeError:
        return False

class RequestExceptionHandler(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
            
        # Code to be executed for each request/response after
        # the view is called.
            
        return response
        
    def process_exception(self, request, exception):
        if is_registered(exception):
            status = exception.status_code
            exception_dict = exception.to_dict()
        else:
            status = 500

            exception_dict = {'errorMessage':
                              'Unexpected Error: {}'.format(exception),
                              #!'traceback': traceback.format_exc(),
            }
        
        #print('DBG: middleware, exception_dict={}'.format(exception_dict))
        #traceback.print_exc()
        return JsonResponse(exception_dict, status=status)
