from util.except_handler import ExecptHadler
from util.utils import Utils
from model.camera import Camera
from threading import Thread
import datetime
import os

class CamController(object):
    # Class-level variables
    __cam_count = 0
    __cams = {}
    __snapshot = {}
    __setting_storage = {}
    __current_setting = ''

    @staticmethod
    def get_cam_count():
        return CamController.__cam_count

    @staticmethod
    def get_current_setting():
        return CamController.__current_setting

    @staticmethod
    def add_camera(camera, autoconnect=False, loop_mode = True):
        host = camera[0]
        port = camera[1]
        user = camera[2]
        passwd = camera[3]
        new_camera = Camera(host,port, user, passwd, autoconnect, loop_mode)
        new_camera.set_name('camera' + str(CamController.__cam_count + 1))
        CamController.__cams[new_camera.get_host()] = new_camera
        CamController.__cam_count += 1

    #@ExecptHadler.safe_func
    @staticmethod
    def get_cam(host):
        get_cam = ''
        #get_cam = Camera(None, None, None, None)
        if host in CamController.__cams:
            get_cam = CamController.__cams[host]
        return get_cam

    @staticmethod
    def load_settings(settingmanager, camera):
        temp_settings = settingmanager.load_setting()
        camera.set_wsdl(temp_settings.get_wsdl_dir())
        CamController.__current_setting = temp_settings #temp_settings.get_name()
        CamController.__setting_storage[temp_settings.get_name()] = temp_settings

    @staticmethod
    def get_snapshot(host):
       #async perform operation
        snap_cam = CamController.__cams[host]
        th_name = 'th_' + str(host) + '_' + str(datetime.datetime.now())
        snapshot_thread = Thread(target=CamController.save_snapshot, args=(host, th_name), name=th_name)
        #snapshot_thread.daemon = True
        snapshot_thread.start()
        #self.save_snapshot(host)

    @staticmethod
    def save_snapshot(host, th_name):
        print 'Thread: ' + th_name + ' start ' + str(datetime.datetime.now())
        snap_cam = CamController.__cams[host]
        snapshot = snap_cam.take_picture()
        if snapshot is not None:
            print 'Response with snapshot: ' + str(snapshot)
            now = datetime.datetime.now()
            pic_dirs = CamController.__setting_storage[CamController.__current_setting.get_name()].get_pic_dir()
            for pic_dir in pic_dirs:
                year = str(now.year)
                month = str(now.month)
                day = str(now.day)
                hour = str(now.hour)
                lastdir = pic_dir
                current_dir = os.path.join(lastdir, year)
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                lastdir = current_dir
                current_dir = os.path.join(lastdir, month)
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                lastdir = current_dir
                current_dir = os.path.join(lastdir, day)
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                lastdir = current_dir
                current_dir = os.path.join(lastdir, hour)
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                lastdir = current_dir
                current_dir = os.path.join(lastdir, host)
                if not os.path.exists(current_dir):
                    os.mkdir(current_dir)
                out = open(current_dir + os.sep + day + '.' + month + '.' + year + ' ' +
                           str(now.hour) + '.' + str(now.minute) + '.' + str(now.second)
                           + ".jpg", "wb")
                out.write(snapshot.content)
                out.close()
                print 'Thread: ' + th_name + ' finish ' + str(datetime.datetime.now())
        else:
            print 'snapshot is None'
            print 'Thread: ' + th_name + ' failed finish ' + str(datetime.datetime.now())

    @staticmethod
    def get_settings():
        return CamController.__settingtorage

    @staticmethod
    def get_setting(name):
        return CamController.__settingtorage[name]