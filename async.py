from threading import Thread

class Async:
    def __init__(self):
        self.threads = list()
        self.daemons = list()

    def __del__(self):
        for t in self.threads:
            t.join()

        for d in self.daemons:
            d.join()

    def start_daemon(self, func, args=None):
        d = Thread(target=func,args=args)
        self.daemons.append(d)
        d.setDaemon(True)
        d.start()

    def async_request(request_func, success_handler=None, error_handler=None, args=None):

        def runner():
            try:
                response = request_func(*args if args else None)
                success_handler(response)
            except Exception as e:
                print(str(e))
                error_handler(response)


        th = Thread(target=runner)
        self.threads.append(th)
        th.start()

