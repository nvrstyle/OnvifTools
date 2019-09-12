from util.except_handler import ExecptHadler


class Service(object):

    def __init__(self, camera_instance, callback=None):

        self.__camera_instance = camera_instance
        self.__connection = 0 #self.__camera_instance.get_connection()
        self.__callback = []
        self.__callback_count = 0
        self.__loop_state = 32

        print "Hallo oypta first" + str(self.__loop_state)
        self.__loop_state = True
        if callable(callback):
            self.add_callback(callback)

    def get_instance(self):
        return self

    def get_camera_instance(self):
        return self.__camera_instance

    def set_connection(self, connection):
        self.__connection = connection

    def get_connection(self):
        return self.__connection

    def add_callback(self, callback):
        if callable(callback):
            self.__callback.append(callback)
            self.__callback_count += 1

    def get_callback_count(self):
        return self.__callback_count

    def get_host_cam(self):
        if self.__connection is not None:
            return self.__connection

    def set_loop_state(self, loop_state):
        self.__loop_state = loop_state

    def get_loop_state(self):
        return self.__loop_state


    @ExecptHadler.safe_func
    def create_service(self):
        pass

    @ExecptHadler.safe_func
    def loop(self):
        pass