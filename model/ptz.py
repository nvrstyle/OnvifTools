from onvif import ONVIFError

from util.except_handler import ExecptHadler
from service import Service
from time import sleep

class PTZ(Service):
    def __init__(self, camera_instance, start_preset = 0, count_preset = 0, end_preset = 0, timeout = 20, persist=False, callback=None):

        self.__ptz_service = None
        self.__ptz_configuration_options = None
        self.__axis = {'Xmax' : None,
                       'Xmin' : None,
                       'Ymax' : None,
                       'Ymin' : None
                      }
        self.__start_preset = start_preset
        self.__count_preset = count_preset
        self.__end_preset = end_preset
        self.__preset_timeout = timeout
        self.__virtual_tours = []
        self.__goto_request = None
        self.__presets = []
        self.__last_preset = start_preset
        self.__service_presets = []
        self.__preset_count = 0
        self.__tours = []

        Service.__init__(self, camera_instance, persist, callback)

    @ExecptHadler.safe_func
    def create_service(self):

        self.__ptz_service = super(PTZ, self).get_connection().create_ptz_service()

        media = super(PTZ, self).get_connection().create_media_service()
        # Get target profile
        media_profile = media.GetProfiles()[0]
        # print 'get media profile: ' + str(media_profile)
        # Get PTZ configuration options for getting continuous move range
        request = self.__ptz_service.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration._token
        self.__ptz_configuration_options = self.__ptz_service.GetConfigurationOptions(request)
        print 'ptz configuration: ' + str(self.__ptz_configuration_options)
        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        self.__axis['XMax'] = self.__ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.__axis['XMin'] = self.__ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.__axis['YMax'] = self.__ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.__axis['YMin'] = self.__ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

        self.__goto_request = self.__ptz_service.create_type('GotoPreset')
        self.__goto_request.ProfileToken = media_profile._token


        self._service_preset = [16, 30, 31, 32, 33, 34, 35, 36,
                                38, 39, 41, 42, 63, 75, 76, 77,
                                78, 81, 82, 83, 84, 85, 91, 92,
                                93, 94, 95, 96, 97, 98, 99]
        print 'Success create PTZ service'

    def add_callback(self, callback):
        super(PTZ, self).add_callback(callback)

    def set_start_preset(self, start_preset):
        super(PTZ, self).stop_loop()
        self.__start_preset = start_preset
        super(PTZ, self).start_loop()

    def get_start_preset(self):
        return self.__start_preset

    def set_count_preset(self, count_preset):
        self.__count_preset = count_preset

    def get_count_preset(self):
        return self.__count_preset

    def set_end_preset(self, end_preset):
        super(PTZ, self).stop_loop()
        self.__end_preset = end_preset
        super(PTZ, self).start_loop()

    def get_end_preset(self):
        return self.__end_preset

    def set_preset_timeout(self):
        self.__preset_timeout

    def get_preset_timeout(self):
        return self.__preset_timeout

    def get_loop_state(self):
        return super(PTZ, self).get_loop_state()

    def get_last_preset(self):
        return self.__last_preset

    def start_loop(self):
        super(PTZ, self).start_loop()

    def stop_loop(self):
        super(PTZ, self).stop_loop()

    @ExecptHadler.safe_func
    def loop(self):
        i = self.__start_preset
        self.__last_preset = i
        end = self.__end_preset
        print "Start preset: " + str(i)
        print "End preset: " + str(end)
        print 'Loop state in loop cycle: ' + str(self.get_loop_state())
        while self.get_loop_state():
            try:
                if self.__count_preset > 0 or self.__end_preset > 0:
                    camera_instance = super(PTZ, self).get_camera_instance()
                    type_camera_instance = type(camera_instance)
                    event_service = camera_instance.get_events_service()
                    ptz_service = camera_instance.get_ptz_service()
                    args = (camera_instance, {'Events': event_service,
                                              'PTZ': ptz_service
                                              })
                    kwargs = {'Camera': camera_instance,
                              'Services': {'Events': event_service,
                                           'PTZ': ptz_service
                                           }
                              }
                    print 'start inside PTZ loop'
                    if len(self.__service_presets) == 0 or self.__service_preset.count(i) == 0:
                        print 'preset number: ' + str(i)
                        self.__goto_request.PresetToken = str(i)
                        self.__ptz_service.GotoPreset(self.__goto_request)
                        print 'jump to preset ' + str(i) + ' and sleep'
                        sleep(self.__preset_timeout/2)
                        print 'time for execute your callback'

                        j = 1
                        for callback in super(PTZ, self).get_callbacks():
                            callback(*args, **kwargs)
                            print 'PTZ callback number ' + str(i) + ' done'
                            j += 1
                        sleep(self.__preset_timeout/2)

                    else:
                        print 'service preset number: ' + str(i)
                    i = i + 1

                    if self.__end_preset == 0 and self.__count_preset !=0:
                        end = self.__start_preset + self.__count_preset

                    if i == end:
                        i = self.__start_preset

                    self.__last_preset = i
                    from controller.setting_controller import SettingController
                    if super(PTZ, self).get_persist_state():
                        print 'Before persist message'
                        SettingController.persist_object(self)
                        print 'After persist message'
                else:
                    print 'EMPTY PRESETS'
            except ONVIFError as e:
                print 'Error inside event loop: ' + str(e.code) + ' reason: ' + str(e.reason)
                super(PTZ, self).stop_loop()


class Tour(object):
    def __init__(self, const_timeout=20, *presets):
        self.__presets = presets
        self.__count = len(presets)
        self.__state = {

                       }
        self.__var_timeout = []
        self.__const_timeout = const_timeout
        pass



class Preset(object):

    def __init__(self, token, name, position):
        self.__token = token
        self.__name = name
        self.__position = position
        pass

    def set_token(self, token):
        self.__token = token

    def get_token(self):
        return self.__token

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_position(self, position):
        self.__position = position

    def get_position(self):
        return self.__position

    def __str__(self):
        return str(self.__token) + ' ' + str(self.__name) + ' ' + str(self.__position)