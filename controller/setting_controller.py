import sys
import os
from model.setting import Setting
from model.events import Events
from controller.cam_controller import CamController
from util.except_handler import ExecptHadler
import datetime



class SettingController(object):
    def __init__(self, name, format_setting = None):
        self.__name = name
        self.__setting_storage = []
        self.__format_setting = format_setting
        self.__default_setting = {'wsdl_dir'   : '',
                                  'work_dir'   : '',
                                  'pic_dir'    : [],
                                  'log_dir'    : '',
                                  'event_dir'  : '',
                                  'setting_dir': ''
                                 }
        if not format_setting:
            self.generate_default_setting()
        if format_setting is 'json':
            print 'do something with json'
        if format_setting is 'xml':
            print 'do something with xml'
        if format_setting is 'csv':
            print 'do something with csv'
        if format_setting is 'txt':
            print 'do something with plain text'

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def get_setting(self):
        pass

    @ExecptHadler.safe_func
    def generate_default_setting(self):
        platform = sys.platform
        #path for windows family
        if platform == 'win32':
            #make work dir
            work_dir = os.getcwd()
            self.__default_setting['work_dir'] = work_dir
            #make log dir
            log_dir = os.path.join(work_dir, 'log')
            self.__default_setting['log_dir'] = log_dir
            if not os.path.exists(log_dir):
                os.mkdir('log')

            #make event dir
            event_dir = os.path.join(work_dir, 'event')
            self.__default_setting['event_dir'] = event_dir
            if not os.path.exists(event_dir):
                os.mkdir('event')
            # make setting dir
            setting_dir = os.path.join(work_dir, 'setting')
            self.__default_setting['setting_dir'] = setting_dir
            if not os.path.exists(setting_dir):
                os.mkdir('setting')
            # make pic dir
            if os.path.exists('C:'):
                print 'disk C exist'
                temp_pic_dir = os.path.join(work_dir, 'snapshot')
                if not os.path.exists(temp_pic_dir):
                    os.mkdir('snapshot')
                self.__default_setting['pic_dir'].append(temp_pic_dir)
                print 'default setting pic_dir: ' + str(self.__default_setting['pic_dir'][0])
            #if os.path.exists('D:'):
            #    print 'disk D exist'
            wsdl_dir = os.path.join(work_dir, 'wsdl')
            if not os.path.exists(wsdl_dir):
                wsdl_dir = ''
                raise Exception("wsdl dir doesn't exist")
            else:
                self.__default_setting['wsdl_dir'] = wsdl_dir

    @staticmethod
    def make_dir(last, current):
        last_dir = last
        current_dir = os.path.join(last_dir, current)
        if not os.path.exists(current_dir):
            os.mkdir(current_dir)
        last_dir = current_dir
        return last_dir

    @staticmethod
    def create_dir_structure(obj_dir, obj_host):
        now = datetime.datetime.now()
        year = str(now.year)
        month = str(now.month)
        day = str(now.day)
        hour = str(now.hour)
        host = obj_host

        dirs = []
        dirs.append(year)
        dirs.append(month)
        dirs.append(day)
        dirs.append(hour)
        dirs.append(host)

        for dir in dirs:
            obj_dir = SettingController.make_dir(obj_dir, dir)
        print 'obj_dir after make dir structure:' + str(obj_dir)
        return now, obj_dir

    @staticmethod
    def persist_object(obj):
       if isinstance(obj, Events):
          event_dir = CamController.get_current_setting().get_event_dir()
          host = obj.get_connection().host
          now, save_dir = SettingController.create_dir_structure(event_dir, host)
          out = open(save_dir + os.sep + str(now.day) + '.' + str(now.month) + '.' + str(now.year) + ' ' + \
                     str(now.hour) + '.' + str(now.minute) + '.' + str(now.second) + '_event'
                         + ".txt", "wt")
          message = str(obj.get_last_event())
          out.write(message)
          out.close()


    def set_default_setting(self, *args):
        pass

    def update_setting(self):
        #if not self.__f_setting:
        pass

    def load_setting(self):
        #if self.__format_setting is None:
        #    settings = SettingStorage('default', **self.__default_setting)
        settings = Setting('default', **self.__default_setting)
        return settings