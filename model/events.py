from util.except_handler import ExecptHadler
from service import Service
from onvif import ONVIFError

class Events(Service):
    def __init__(self, camera_instance, persist=False, callback=None, event_limit=10):
        self.__event_limit = event_limit
        self.__event_storage = []
        self.__events_service = None
        self.__pullpoint_service = None
        self.__event_request = None
        Service.__init__(self, camera_instance, persist, callback)

    def get_event_storage(self):
        return self.__event_storage

    def get_last_event(self):
        return self.__event_storage[len(self.__event_storage)-1]

    def get_message_count(self):
        return self.__event_storage.count()

    @ExecptHadler.safe_func
    def create_service(self):
        super(Events, self).get_connection().create_events_service()
        self.__events_service = super(Events, self).get_connection().create_pullpoint_service()
        self.__event_request = self.__events_service.create_type('PullMessages')
        self.__event_request.MessageLimit = 1
        self.__event_request.Timeout = 'PT1M'

    def add_callback(self, callback):
        super(Events, self).add_callback(callback)

    @ExecptHadler.safe_func
    def loop(self):
        while True:
            try:
                camera_instance = super(Events, self).get_camera_instance()
                type_camera_instance = type(camera_instance)
                event_service = camera_instance.get_events_service()
                ptz_service = camera_instance.get_ptz_service()
                args = (camera_instance, {'Events' : event_service,
                                          'PTZ'    : ptz_service
                                         })
                kwargs = {'Camera'   : camera_instance,
                          'Services' : { 'Events' : event_service,
                                         'PTZ'    : ptz_service
                                       }
                         }
                print 'start inside event loop'
                print 'Type of camera instance: ' + str(type_camera_instance)
                resp = self.__events_service.PullMessages(self.__event_request)
                print 'success get event response'
                name = str(resp.NotificationMessage[0].Message[0].Data.SimpleItem._Name)
                print 'success parse event name'
                timestamp = str(resp.CurrentTime)
                print 'success parse event timestamp'
                data = str(resp.NotificationMessage[0].Message[0].Data.SimpleItem._Value)
                print 'success parse event data'
                new_event = Event(name, timestamp, data)
                print 'success create Event data structure'
                if len(self.__event_storage) == self.__event_limit:
                    print 'inside if event storage count'
                    print 'Storage is full'
                    self.__event_storage = []
                    print 'success clear event storage'
                self.__event_storage.append(new_event)
                print 'success append event in storage'
                from controller.setting_controller import SettingController
                if super(Events, self).get_persist_state():
                    print 'Before persist message'
                    SettingController.persist_object(self)
                    print 'After persist message'

                print 'time for execute your callback'
                i = 1
                for callback in super(Events, self).get_callbacks():
                    callback(*args, **kwargs)
                    print 'callback number ' + str(i) + ' done'
                    i += 1
            except ONVIFError as e:
                print 'Error inside event loop: ' + str(e.code) + ' reason: ' + str(e.reason)

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