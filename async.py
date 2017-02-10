from threading import Thread

class Async:
    def __init__(self):
        self.threads = list()
        self.daemons = list()

    def __del__(self):
        for t in self.threads:
            t.join()

    def start_daemon(self, func, args=None):
        d = Thread(target=func,args=args)
        d.setDaemon(True)
        d.start()
        self.daemons.append(d)

    def async_request(request_func, 
            success_handler=None, 
            error_handler=None, 
            args=None):

        def runner():
            try:
                response = request_func(*args if args else None)
            except:
                error_handler(response)
                return

            success_handler(response)

        th = Thread(target=runner)
        self.threads.append(th)
        th.start()

