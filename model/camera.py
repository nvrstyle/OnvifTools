from util.except_handler import ExecptHadler
from onvif import ONVIFCamera
import requests

class Camera(object):
    #wsdl
    __wsdl = ''

    def __init__(self, host, port, user, passwd, daemon_conn = False):
        if host is not None and port is not None and user is not None and passwd is not None:
            self.__host = host
            self.__port = int(port)
            self.__user = user
            self.__passw = passwd
            self.__snapshot_url = ''
            self.__snapshot_resolution = 'HIGH'
            self.__onvif_v = ''
            self.__connection = None
            self.__daemon_conn = daemon_conn
            self.__connect_state = False
            self.__name = ''
            self.__services = { 'Event' : None,
                                'PTZ'   : None
                              }

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

    def __set_connection(self, connection):
        self.__connection = connection

    def get_connection(self):
        if not self.__connection:
            self.up_connect()
        return self.__connection

    def get_services(self):
        return self.__services

    def get_event_service(self):
        return self.__services['Event']

    def get_ptz_service(self):
        return self.__services['PTZ']

    @ExecptHadler.safe_func
    def up_connect(self):
        print 'Enter inside up_connect function'
        print 'wsdl state inside up_connect function: ' + str(self.__wsdl)
        if self.__wsdl:
            print 'Before connect,Inside connection function camera ' + str(self.__host)
            print 'Before connect, connect_state: ' + str(self.__connect_state)
            print 'Before connect variable connection: ' + str(self.__connection)
            self.__connection = ONVIFCamera(self.__host, self.__port,
                                self.__user, self.__passw, self.__wsdl, None, None, True, self.__daemon_conn, False, False) #, no_cache=True)
            print 'After connect, Inside connection function camera ' + str(self.__host)
            self.__connect_state = True
            print 'After connect, connect_state: ' + str(self.__connect_state)
            print 'After connect variable connection: ' + str(self.__connection)
                #compatibility_services()
        else:
            print "Don't define wsdl"
            self.__connect_state = False

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

    def take_picture(self, daemon = False):
        resp = requests.get(self.get_snapshot_url(), auth=(self.__user, self.__passw))
        return resp#.content