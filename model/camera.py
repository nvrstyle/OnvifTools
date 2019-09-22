import re
from types import NoneType

from util.except_handler import ExecptHadler
from util.utils import Utils
from analytics import Analytics
from device import Device
from events import Events
from imaging import Imaging
from media import Media
from ptz import PTZ
from service import Service
from onvif import ONVIFCamera
from onvif import ONVIFError
from onvif import ONVIFService
from onvif import SERVICES
import requests
from threading import Thread


class Camera(object):
    # wsdl
    __wsdl = ''

    def __init__(self, host, port, user, passwd, autoconnect=False, loop_mode=False, daemon_conn=False):
        if host is not None and port is not None and user is not None and passwd is not None:
            self.__host = host
            self.__port = int(port)
            self.__user = user
            self.__passwd = passwd
            self.__autoconnect = autoconnect
            self.__loop_mode = loop_mode

            self.__device_info = {'Manufacturer': '',
                                  'Model': '',
                                  'FirmwareVersion': '',
                                  'SerialNumber': '',
                                  'HardwareId': ''
                                  }
            self.__snapshot_url = ''
            self.__snapshot_resolution = 'HIGH'
            self.__onvif_v = ''
            self.__connection = None
            self.__daemon_conn = daemon_conn
            self.__connect_state = False
            self.__try_connect = False
            self.__name = ''
            self.__count_services = 0
            self.__raw_services = []
            self.__services = {'Analytics': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'Device': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'DeviceIO': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'Events': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'Imaging': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'Media': ({'support': False}, {'init': False}, {'run': False}, {'instance': None}),
                               'PTZ': ({'support': False}, {'init': False}, {'run': False}, {'instance': None})
                               }
            if self.__autoconnect:
                print "Autoconnect is True"
                # thread_connect = Thread(target=self.up_connect,
                #                        name='thread_connect_' + str(self.__host))
                # thread_connect.start()
                self.up_connect()
            else:
                print "Autoconnect is False"

            if self.__loop_mode:
                print "Loop mode is True"
                thread_loop = Thread(target=self.loop,
                                     name='thread_loop_' + str(self.__host))
                thread_loop.start()
            else:
                print "Loop mode is False"


    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_host(self, host):
        self.__host = host

    def get_host(self):
        return self.__host

    def set_snapshot_url(self, snapshot_url):
        self.__snapshot_url = snapshot_url

    def get_snapshot_url(self):
        if not self.__snapshot_url:
            self.update_snapshot_url()
        return self.__snapshot_url

    def set_onvif_v(self, onvif_v):
        self.__onvif_v = onvif_v

    def get_onvif_v(self):
        if not self.__onvif_v:
            self.update_onvif_v()
        return self.__onvif_v

    @staticmethod
    def set_wsdl(wsdl_path):
        Camera.__wsdl = wsdl_path

    @staticmethod
    def get_wsdl():
        return Camera.__wsdl

    def set_connection(self, connection):
        self.__connection = connection

    def get_connection(self):
        if not self.__connection:
            self.up_connect()
        return self.__connection

    def get_services(self):
        return self.__services

    def get_analytics_service(self):
        return self.__services['Analytics']

    def get_device_service(self):
        return self.__services['Device']

    def get_events_service(self):
        return self.__services['Events'][3]['instance']

    def get_imaging_service(self):
        return self.__services['Imaging']

    def get_media_service(self):
        return self.__services['Media']

    def get_ptz_service(self):
        return self.__services['PTZ'][3]['instance']

    def get_ptz_service_full(self):
        return self.__services['PTZ']

    def get_connect_state(self):
        return self.__connect_state

    def up_connect(self):
        i = 1
        while True:
            try:
                # print 'Try connect ' + str(i) + ' , connect is: ' + str(self.__connect_state)
                # print 'Enter inside up_connect function'
                # print 'wsdl state inside up_connect function: ' + str(self.__wsdl)
                if self.__wsdl:
                    # print 'Before connect,Inside connection function camera ' + str(self.__host)
                    # print 'Before connect, connect_state: ' + str(self.__connect_state)
                    # print 'Before connect variable connection: ' + str(self.__connection)
                    self.__connection = ONVIFCamera(self.__host, self.__port,
                                                    self.__user, self.__passwd, self.__wsdl, None, None, True,
                                                    self.__daemon_conn, False, False)  # , no_cache=True)
                    # print 'After connect, Inside connection function camera ' + str(self.__host)
                    self.__connect_state = True
                    self.__try_connect = False
                    self.__get_raw_services()
                    self.__get_raw_device_info()
                    # print 'After connect, try_connect: ' + str(self.__try_connect)
                    # print 'After connect, connect_state: ' + str(self.__connect_state)
                    # print 'After connect variable connection: ' + str(self.__connection)
                    break
                    # compatibility_services()
                else:
                    print "Don't define wsdl"
                    self.__connect_state = False

            except ONVIFError as e:
                self.__connect_state = False

                print 'exception: ' + str(e.reason)
                continue
            i += 1

    def loop(self):
        i = 1
        print "In camera_" + str(self.__host) + " loop"
        while True:
            try:
                if isinstance(self.__connection, ONVIFCamera) and self.__connect_state:
                    self.get_support_service()
                    self.loop_edit_init_sll_services()
                    while True:
                        self.loop_check_edit_instance_all_service()
                        #print 'PTZ Service states: ' + str(self.__services['PTZ'])

                        # print "Connection is True"
                        # print "Something doing in camera loop..."
                        pass
                else:
                    if not isinstance(self.__connection, ONVIFCamera) or not self.__connect_state:
                        # print 'The connection has not yet been established or connection has been lost'
                        self.try_connect(i)
            except ONVIFError as e:
                self.__connect_state = False
                print 'Exception inside loop: ' + str(e.reason)
                self.try_connect(i)
                continue
            i += 1

    def update_onvif_v(self):
        pass

    @ExecptHadler.safe_func
    def compatibility_services(self):
        pass

    @ExecptHadler.safe_func
    def update_snapshot_url(self):
        media = self.get_connection().create_media_service()
        allProfiles = media.GetProfiles()
        mainProfile = media.GetProfile({'ProfileToken': allProfiles[0]._token})
        secondProfile = media.GetProfile({'ProfileToken': allProfiles[1]._token})
        snapshot_url_main = media.GetSnapshotUri({'ProfileToken': mainProfile._token})
        snapshot_url_second = media.GetSnapshotUri({'ProfileToken': secondProfile._token})
        self.__snapshot_url = snapshot_url_main.Uri
        pass

    def get_device_info(self):
        return self.__device_info


    #@Utils.async_func
    def __get_raw_device_info(self):
        i = 1
        while True:
            try:
                if isinstance(self.__connection, ONVIFCamera) and self.__connect_state:
                    device_info = self.__connection.devicemgmt.GetDeviceInformation()
                    self.__device_info['Manufacturer'] = str(device_info.Manufacturer)
                    self.__device_info['Model'] = str(device_info.Model)
                    self.__device_info['FirmwareVersion'] = str(device_info.FirmwareVersion)
                    self.__device_info['Serial Number'] = str(device_info.SerialNumber)
                    self.__device_info['HardwareId'] = str(device_info.HardwareId)
                    print str(self.__device_info)
                    break
                else:
                    if not isinstance(self.__connection, ONVIFCamera) or not self.__connect_state:
                        #print 'The connection has not yet been established or connection has been lost'
                        self.try_connect(i)
            except ONVIFError as e:
                self.__connect_state = False
                print 'exception inside get_device_info: ' + str(e.reason)
                print 'Connection is None'
                self.try_connect(i)
                continue
        i += 1
        return self.__device_info

    def take_picture(self, daemon=False):
        resp = requests.get(self.get_snapshot_url(), auth=(self.__user, self.__passwd))
        return resp  # .content

    def loop_check_status_abstract_service(self, status, name_service, service_instance=None):
        local_vars = locals()
        local_vars = local_vars.values()
        # print ('Name of Vars:' + str(local_vars))
        status_var_str = local_vars[0]
        name_service_str = local_vars[1]
        # print 'status name: ' + str(status_var_str)
        # print 'name service:' + str(name_service_str)
        support = self.__services[name_service][0]['support']
        # print 'support: ' + str(support)
        init = self.__services[name_service][1]['init']
        # print 'init: ' + str(init)
        run = self.__services[name_service][2]['run']
        # print 'run: ' + str(run)
        instance = self.__services[name_service][3]['instance']
        # print 'instance: ' + str(instance)
        check_status = False

        if self.__loop_mode:
            if status_var_str == 'support':
                if support:
                    check_status = True
                    #print 'PTZ SERVICE CHECK STATUS <SUPPORT> :' + str(check_status)
                    #print 'Service ' + str(name_service) + ' already support'

            if status_var_str == 'init':
                if support and init:
                    check_status = True
                    #print 'PTZ SERVICE CHECK STATUS <INIT> :' + str(check_status)
                    #print 'Service ' + str(name_service) + ' already init'

            if status_var_str == 'run':
                if init and run:
                    check_status = True
                    #print 'Service ' + str(name_service) + ' already run'
                    #print 'PTZ SERVICE CHECK STATUS <RUN> :' + str(check_status)

            if status_var_str == 'instance':
                if run and instance is not None:
                    check_status = True
                    #print 'PTZ SERVICE CHECK STATUS <INSTANCE> :' + str(check_status)
                    #print 'Instance ' + str(name_service) + ' service already exists'

        return check_status

    def loop_edit_status_abstract_service(self, status, name_service, service_instance=None):
        #print "Run loop_edit_status_abstract_service(run, Events) from run_abstract_service(Events, persist)"
        #print 'RUN<> ' + str(name_service) + ' service'
        local_vars = locals()
        local_vars = local_vars.values()
        #print ('Name of Vars:' + str(local_vars))
        status_var_str = local_vars[0]
        name_service_str = local_vars[1]
        #print 'status name: ' + str(status_var_str)
        #print 'name service:' + str(name_service_str)
        support = self.__services[name_service][0]['support']
        #print 'support: ' + str(support)
        init = self.__services[name_service][1]['init']
        #print 'init: ' + str(init)
        run = self.__services[name_service][2]['run']
        #print 'run: ' + str(run)
        instance = self.__services[name_service][3]['instance']
        #print 'instance: ' + str(instance)

        #print 'LOOP MODE: ' + str(self.__loop_mode)
        if self.__loop_mode:
            if status_var_str == 'support':
                if not support:
                    self.__services[name_service][0]['support'] = True
                    #print 'change state support True PTZ in loop_edit_status_abstract_service'
                else:
                    print 'Service ' + str(name_service) + ' already support'

            if status_var_str == 'init':
                if support and not init:
                    self.__services[name_service][1]['init'] = True
                    #print 'change state init True PTZ in loop_edit_status_abstract_service'
                #else:
                #    if not support:
                #       print 'Service ' + str(name_service) + ' not support in loop_edit_status_abstract_service, connection_state: ' + str(self.__connect_state)

            if status_var_str == 'run':
                #print "status_var_str == run in loop_edit_status_abstract_service(run, Events)"
                if init and not run:
                    #print "inside if init and not run in loop_edit_status_abstract_service(run, Events)"
                    self.__services[name_service][2]['run'] = True
                    #print 'change state run True PTZ in loop_edit_status_abstract_service'
                #else:
                #   print 'Service ' + str(name_service) + ' already run'

            if status_var_str == 'instance':
                if run is not None and instance is None and service_instance is not None:
                    self.__services[name_service][3]['instance'] = service_instance
                    #print 'change state instance PTZ class object in loop_edit_status_abstract_service' + str(
                    #   service_instance)
                #else:
                #   print 'Instance ' + str(name_service) + ' service already exists'

    def loop_support_abstract_service(self, name_service):
        #print 'In loop_support_abstract_service'
        self.loop_edit_status_abstract_service('support', name_service)

    def loop_init_abstract_service(self, name_service):
        self.loop_edit_status_abstract_service('init', name_service)

    def loop_run_abstract_service(self, name_service):
        self.loop_edit_status_abstract_service('run', name_service)

    def loop_instance_abstract_service(self, name_service):
        self.loop_edit_status_abstract_service('instance', name_service)

    def loop_check_edit_instance_service(self, name_service):
        run = self.loop_check_status_abstract_service('run', name_service)
        instance = self.loop_check_status_abstract_service('instance', name_service)
        #print 'NAME PTZ SERVICE BEFORE IF:' + str(name_service)
        #print 'NAME PTZ SERVICE RUN:' + str(run)
        #print 'NAME PTZ SERVICE INSTANCE:' + str(instance)

        #instance_service = None
        #instance_flag = False
        if run and not instance:
            if name_service == 'Analytics':
                instance_service = Analytics(self, True)
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
            if name_service == 'Device':
                instance_service = Device(self, True)
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
            if name_service == 'Events':
                instance_service = Events(self, True)
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
            if name_service == 'Imaging':
                instance_service = Imaging(self, True)
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
            if name_service == 'Media':
                instance_service = Media(self, True)
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
            if name_service == 'PTZ':
                #print 'MY<>NAME<>PTZ'
                instance_service = PTZ(self,0,0,0,20,True,None)
                #print 'Vse NORM'
                self.loop_edit_status_abstract_service('instance', name_service, instance_service)
                instance_flag = True
        #return instance_flag, instance_service

    #@Utils.async_func
    def loop_edit_init_sll_services(self):
        self.loop_edit_init_analytics_service()
        self.loop_edit_init_device_service()
        self.loop_edit_init_events_service()
        self.loop_edit_init_imaging_service()
        self.loop_edit_init_media_service()
        self.loop_edit_init_ptz_service()

    #@Utils.async_func
    def loop_check_edit_instance_all_service(self):
        self.loop_check_edit_instance_service('Analytics')
        self.loop_check_edit_instance_service('Device')
        self.loop_check_edit_instance_service('Events')
        self.loop_check_edit_instance_service('Imaging')
        self.loop_check_edit_instance_service('Media')
        self.loop_check_edit_instance_service('PTZ')

    @Utils.async_func
    def loop_edit_init_analytics_service(self):
        self.loop_init_abstract_service('Analytics')

    @Utils.async_func
    def loop_edit_init_device_service(self):
        self.loop_init_abstract_service('Device')

    @Utils.async_func
    def loop_edit_init_events_service(self):
        self.loop_init_abstract_service('Events')

    @Utils.async_func
    def loop_edit_init_imaging_service(self):
        self.loop_init_abstract_service('Imaging')

    @Utils.async_func
    def loop_edit_init_media_service(self):
        self.loop_init_abstract_service('Media')

    @Utils.async_func
    def loop_edit_init_ptz_service(self):
        self.loop_init_abstract_service('PTZ')

    def __get_raw_services(self):
        self.__raw_services = self.__connection.devicemgmt.GetServices({'IncludeCapability': False})
        if type(self.__raw_services) is not None:
            self.__count_services = len(self.__raw_services)

    def get_raw_services(self):
        return self.__raw_services

    def get_count_services(self):
        return self.__count_services

    def get_device_services(self):
        if self.__count_services != 0:
            for j in range(self.__count_services):
                service = self.__raw_services[j].Namespace
                #print 'support_service[j].Namespace:' + str(self.__raw_services[j].Namespace)
                result = re.findall(r'http://www.onvif.org/ver[0-9]*/([a-z]*[A-Z]*)/wsdl', str(service))
                #print 'Result Regexp: ' + result[0]
                yield str(result[0])


    #@Utils.async_func
    def get_support_service(self):
        i = 1
        while True:
            try:
                if isinstance(self.__connection, ONVIFCamera) and self.__connect_state:
                    if self.__count_services != 0:
                        #for j in range(self.__count_services):
                        for j in self.get_device_services():
                            name_service = j
                            if name_service == 'analytics':
                                name_service = 'Analytics'
                            if name_service == 'device':
                                name_service = 'Device'
                            if name_service == 'events':
                                name_service = 'Events'
                            if name_service == 'imaging':
                                name_service = 'Imaging'
                            if name_service == 'media':
                                name_service = 'Media'
                            if name_service == 'deviceIO':
                                name_service = 'DeviceIO'
                            if name_service == 'ptz':
                                name_service = 'PTZ'
                            self.loop_support_abstract_service(name_service)
                        break
                    else:
                        print 'Type of support_services is None in get_support_service'
                else:
                    if not isinstance(self.__connection, ONVIFCamera) or not self.__connect_state:
                        # print 'The connection has not yet been established or connection has been lost'
                        self.try_connect(i)
            except ONVIFError as e:
                self.__connect_state = False
                print 'Exception inside get_support_device: ' + str(e.reason)

                self.try_connect(i)
                continue
            i += 1

    def try_connect(self, i=1):
        if not self.__try_connect:
            self.__try_connect = True
            self.up_connect()
        #    print 'Try connect ' + str(i) + ' , connect is: ' + str(self.__connect_state)
        # else:
        #    print 'Already trying connect ' + str(i) + ' , connect is: ' + str(self.__connect_state)

    @Utils.async_func
    def run_all_services(self, persist=False):
        self.run_abstract_service('Analytics', persist)
        self.run_abstract_service('Device', persist)
        self.run_abstract_service('Events', persist)
        self.run_abstract_service('Imaging', persist)
        self.run_abstract_service('Media', persist)
        self.run_abstract_service('PTZ', persist)

    @Utils.async_func
    def run_analytics_service(self, persist=False):
        self.run_abstract_service('Analytics', persist)

    @Utils.async_func
    def run_device_service(self, persist=False):
        self.run_abstract_service('Device', persist)

    @Utils.async_func
    def run_events_service(self, persist=False):
        #print "run run_events_service from agent.py"
        self.run_abstract_service('Events', persist)
        #print "after call run_abstract_service(Events, persist) from run_events_service(persist)"

    @Utils.async_func
    def run_imaging_service(self, persist=False):
        self.run_abstract_service('Imaging', persist)

    @Utils.async_func
    def run_media_service(self, persist=False):
        self.run_abstract_service('Media', persist)

    @Utils.async_func
    def run_ptz_service(self, persist=False):
        print 'run_ptz_service'
        self.run_abstract_service('PTZ', persist)

    @Utils.async_func
    def run_abstract_service(self, service_name, persist=False):
        #print "run run_abstract_service(Events, persist) from run_events_service(self, persist=False)"
        i = 1
        service_instance = None
        while True:
            try:
                if isinstance(self.__connection, ONVIFCamera) and self.__connect_state:
                    #print 'Run ' + str(service_name) + ' service'
                    support = self.loop_check_status_abstract_service('support', service_name)
                    init = self.loop_check_status_abstract_service('init', service_name)
                    #run = self.loop_check_status_abstract_service('run', service_name)
                    if self.__loop_mode:
                        if support and init:
                            #print 'change state run True ' + str(service_name) + ' service'
                            #print "Call loop_edit_status_abstract_service(run, Events) from run_abstract_service(Events, persist)"
                            self.loop_edit_status_abstract_service('run', service_name)
                    else:
                        print 'Start ' + str(service_name) + ' service'
                        # self.__services['Event'] = EventService(self.__connection, persist)
                        self.loop_edit_status_abstract_service('run', service_name)
                        if service_name == 'Analytics':
                            service_instance = Analytics(self, persist)
                        if service_name == 'Device':
                            service_instance = Device(self, persist)
                        if service_name == 'Events':
                            service_instance = Events(self, persist)
                        if service_name == 'Imaging':
                            service_instance = Imaging(self, persist)
                        if service_name == 'Media':
                            service_instance = Media(self, persist)
                        if service_name == 'PTZ':
                            service_instance = PTZ(self,0,0,0,20,persist,None)
                        if service_instance is not None:
                            self.loop_edit_status_abstract_service('instance', service_name, service_instance)
                            break
                        else:
                            print 'service_instance of ' + str(service_name) + ' is None'

                else:
                    if not isinstance(self.__connection, ONVIFCamera) or not self.__connect_state:
                        # print 'The connection has not yet been established or connection has been lost'
                        self.try_connect(i)
            except ONVIFError as e:
                self.__connect_state = False
                print 'Exception inside get_support_device: ' + str(e.reason)
                self.try_connect(i)
                continue
            i += 1

