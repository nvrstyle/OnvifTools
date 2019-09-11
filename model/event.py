class Event(object):

    def __init__(self, name='', timestamp='', data=''):
        self.__name = name
        self.__timestamp = timestamp
        self.__data = data

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_timestamp(self, timestamp):
        self.__timestamp = timestamp

    def get_timestamp(self):
        return self.__timestamp

    def set_data(self, data):
        self.__data = data

    def get_data(self):
        return self.__data

    def __str__(self):
        return str(self.__name) + ' ' + str(self.__data) + ' ' + str(self.__timestamp)