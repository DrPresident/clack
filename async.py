from threading import Thread

def async_request(request_func, 
        success_handler=None, 
        error_handler=None, 
        args=None):

    th = Thread(target=request_func, args=(args if args else None))

