class Setting(object):

    def __init__(self, name, **kwargs):
        self.__name = name
        self.__work_dir = kwargs['work_dir']
        self.__pic_dir = []
        self.__pic_dir = kwargs['pic_dir']
        self.__log_dir = kwargs['log_dir']
        self.__wsdl_dir = kwargs['wsdl_dir']
        self.__event_dir = kwargs['event_dir']
        self.__setting_dir = kwargs['setting_dir']

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def get_pic_dir(self):
        return self.__pic_dir

    def set_pic_dir(self, pic_dir):
        self.__pic_dir = pic_dir

    def get_log_dir(self):
        return self.__log_dir

    def set_log_dir(self, log_dir):
        self.__log_dir = log_dir

    def set_work_dir(self, work_dir):
        self.__work_dir = work_dir

    def get_work_dir(self):
        if not self.__work_dir:
            self.update_work_dir()
        return self.__work_dir

    def update_work_dir(self):
        pass

    def set_wsdl_dir(self, work_dir):
        self.__work_dir = work_dir

    def get_wsdl_dir(self):
        if not self.__wsdl_dir:
            self.update_wsdl_dir()
        return self.__wsdl_dir

    def update_wsdl_dir(self):
        pass

    def set_event_dir(self, event_dir):
        self.__event_dir = event_dir

    def get_event_dir(self):
        if not self.__event_dir:
            self.update_event_dir()
        return self.__event_dir

    def update_event_dir(self):
        pass

    def set_setting_dir(self, setting_dir):
        self.__setting_dir = setting_dir

    def get_setting_dir(self):
        if not self.__setting_dir:
            self.update_setting_dir()
        return self.__setting_dir

    def update_setting_dir(self):
        pass

    def __str__(self):
        return str(self.__name) + '\n' + str(self.__work_dir) + '\n' + str(self.__pic_dir) + \
               '\n' + str(self.__log_dir) + '\n' + str(self.__event_dir) + '\n' + str(self.__wsdl_dir) + \
               '\n' + str(self.__setting_dir) + '\n\n'