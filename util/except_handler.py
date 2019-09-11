from onvif import ONVIFError

class ExecptHadler(object):

    def __init__(self):
        pass

    @staticmethod
    def safe_func(self, func):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                raise ONVIFError(err)

        return wrapped
