import logging
import time
import uuid

from colorama import Fore
from requests import Session
from requests.exceptions import ConnectionError as ServerConnectionError
from transitions import Machine
from transitions import State

from camera import CaptureError, ConnectionError
from config import config
from network import UnableToAuthenticateError
from plant import Plant


class PhenoboxMachine(Machine):
    camera_controller = None
    code_scanner = None
    motor_controller = None
    led_controller = None
    image_handler = None
    auth = None
    code_information = None
    plant = None
    pic_count = 0
    error_code = 0

    error_messages = {
        1: "Unable to read QR-Code",
        2: "Unable to upload pictures",
        3: "Door was opened unexpectedly",
        4: "Unable to capture picture",
        5: "Unable to connect to camera",
        6: "Unable to retrieve data",
        7: "Unable to authenticate",
        8: "Unable to get picture from camera",
        9: "Unable to create snapshot on server",
        10: "This plant has already been processed for the current timestamp",
        11: "Unable to connect to server"
    }

    def __init__(self, camera_controller, code_scanner, motor_controller, led_controller, image_handler, auth,
                 photo_count=6):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        states = ['STARTUP',
                  State(name='IDLE', on_enter='on_enter_idle'),
                  State(name='AUTH', on_enter='on_enter_auth'),
                  State(name='TAKE_FIRST_PICTURE', on_enter='on_enter_take_first_picture'),
                  State(name='ANALYZE_PICTURE', on_enter='on_enter_analyze_picture'),
                  State(name='SETUP', on_enter='on_enter_setup'),
                  State(name='DRIVE', on_enter='on_enter_drive'),
                  State(name='TAKE_PICTURE', on_enter='on_enter_take_picture'),
                  State(name='RETURN', on_enter='on_enter_return'),
                  State(name='UPLOAD', on_enter='on_enter_upload'),
                  State(name='ERROR', on_enter='on_enter_error', on_exit='on_exit_error', ignore_invalid_triggers=True)
                  ]

        Machine.__init__(self, states=states, send_event=True, initial="STARTUP")
        self.add_transition('initialize', 'STARTUP', 'RETURN', after=[self.after_return])

        # ----FROM IDLE----#
        self.add_transition('start', 'IDLE', 'SETUP', after=[self.after_start], conditions=[self.valid_authentication])
        self.add_transition('start', 'IDLE', 'AUTH', unless=[self.valid_authentication])
        # ----FROM AUTH----#
        self.add_transition('start', 'AUTH', 'SETUP', after=[self.after_start])
        self.add_transition('error', 'AUTH', 'ERROR')
        # ----FROM TAKE_FIRST_PICTURE----#
        self.add_transition('analyze', 'TAKE_FIRST_PICTURE', 'ANALYZE_PICTURE', after=[self.after_analyze])
        self.add_transition('error', 'TAKE_FIRST_PICTURE', 'ERROR')
        # ----FROM ANALYZE_PICTURE----#
        self.add_transition('rotate', 'ANALYZE_PICTURE', 'DRIVE', after=[self.after_rotate])
        self.add_transition('error', 'ANALYZE_PICTURE', 'ERROR')
        # ----FROM SETUP----#
        self.add_transition('take_first', 'SETUP', 'TAKE_FIRST_PICTURE', after=[self.after_take_first])
        # ----FROM DRIVE----#
        self.add_transition('picture', 'DRIVE', 'TAKE_PICTURE', after=[self.after_picture])
        # ----FROM TAKE_PICTURE----#
        self.add_transition('error', "TAKE_PICTURE", 'ERROR')
        self.add_transition('next_picture', 'TAKE_PICTURE', 'DRIVE', after=[self.after_rotate],
                            unless=[self.enough_pictures])
        self.add_transition('next_picture', 'TAKE_PICTURE', 'UPLOAD', after=[self.after_upload],
                            conditions=[self.enough_pictures])
        # ----FROM RETURN----#
        self.add_transition('idle', 'RETURN', 'IDLE')
        # ----FROM UPLOAD----#
        self.add_transition('upload_finished', 'UPLOAD', 'RETURN', after=[self.after_return])
        # ----FROM ERROR----#
        self.add_transition('restart', 'ERROR', 'SETUP', after=[self.after_start],
                            conditions=[self.valid_authentication])
        self.add_transition('restart', 'ERROR', 'AUTH',
                            unless=[self.valid_authentication])
        # ----DOOR----#
        self.add_transition('door_opened', ['TAKE_FIRST_PICTURE', 'ANALYZE_PICTURE', 'SETUP',
                                            'DRIVE', 'TAKE_PICTURE', 'UPLOAD', 'RETURN', 'AUTH'], 'ERROR')

        self.camera_controller = camera_controller
        self.code_scanner = code_scanner
        self.motor_controller = motor_controller
        self.led_controller = led_controller
        self.image_handler = image_handler
        self.photo_count = photo_count

        self.auth = auth

    def valid_authentication(self, event):
        return self.auth.is_authenticated() or self.auth.can_refresh()

    def on_enter_return(self, event):
        print(Fore.BLUE + 'Returning to Origin')
        # time.sleep(1)
        self.motor_controller.return_to_origin()

    def after_return(self, event):
        self.idle()

    def on_enter_idle(self, event):
        print(Fore.GREEN + 'Idle. Waiting for user Input')
        self.led_controller.clear_all()
        self.led_controller.switch_green(True)
        self.code_information = None
        self.plant = None

    def on_enter_auth(self, event):
        print(Fore.BLUE + 'Authenticating')
        self.led_controller.switch_green(False)
        self.led_controller.switch_blue(True)
        try:
            if self.auth.check_and_auth():
                self.start()
            else:
                self.error(error_code=7)
        except ServerConnectionError as e:
            self._logger.error(e.message)
            self.error(error_code=11)

    def on_enter_setup(self, event):
        print(Fore.BLUE + 'Setting up')
        self.led_controller.switch_green(False)
        self.led_controller.switch_blue(True)
        self.motor_controller.return_to_origin()
        self.plant = Plant()

    def after_start(self, event):
        self.take_first()

    def on_enter_take_first_picture(self, event):
        print(Fore.BLUE + 'Taking first picture')
        try:
            picture_path = self.camera_controller.capture_and_download(name=str(uuid.uuid4()))
            if picture_path is None:
                self.error(error_code=8)
            else:
                self.plant.add_picture(picture_path, self.motor_controller.current_angle)
                self.analyze()
        except ConnectionError as err:
            self._logger.error(err.message)
            self.error(error_code=5)
        except CaptureError as err:
            self._logger.error(err.message)
            self.error(error_code=4)

    def after_take_first(self, event):
        pass
        # self.analyze()

    def on_enter_analyze_picture(self, event):
        print(Fore.BLUE + 'Analyzing')
        path, _ = self.plant.get_first_picture()
        self.code_information = self.code_scanner.scan_image(path)

    def after_analyze(self, event):
        if self.code_information is not None:
            print(Fore.CYAN + 'Decoded ' + str(self.code_information.type) + ' symbol "%s"' % str(
                self.code_information.data))
            self._logger.info(
                'decoded {}, symbol {}'.format(self.code_information.type, str(self.code_information.data)))
            plant_id = self.code_information.data
            try:
                s = Session()
                graphql_address = '{}{}'.format(getattr(config, 'cfg').get('server', 'base_address'),
                                                getattr(config, 'cfg').get('server', 'graphql_endpoint'))
                prepped_req = self.auth.prep_post(graphql_address, data={
                    'query': '{plant(id:"' + plant_id + '"){id index name fullName sampleGroup {name experiment {name}}}}'})
                r = s.send(prepped_req)
                plant = r.json()['data']['plant']
                if plant is None:
                    self.error(error_code=6)
                    return
                else:
                    # Create Snapshot
                    param_string = 'plantId:"{}", cameraPosition:"{}", measurementTool:"{}",phenoboxId:"{}"' \
                        .format(plant['id'],
                                getattr(config, 'cfg').get('box', 'camera_position'),
                                getattr(config, 'cfg').get('box', 'measurement_tool'),
                                getattr(config, 'cfg').get('box', 'id'))
                    prepped_req = self.auth.prep_post(graphql_address, data={
                        'query': 'mutation {createSnapshot(' + param_string + '){id timestampId}}'})
                    r = s.send(prepped_req)
                    if r.status_code != 200:
                        # TODO get exception
                        self._logger.info(
                            'Unable to create Snapshot. HTML status code {}. Param String : {}'.format(
                                r.status_code,
                                param_string))
                        self.error(error_code=9)
                        return
                        # do something
                    resp = r.json()
                    if resp.get('errors', None):
                        if resp.get('errors')[0]['code'] == 409:
                            self._logger.info('Snapshot already exists')
                            self.error(error_code=10)
                        else:
                            self._logger.error(
                                'Error while trying to create snapshot. Param String : {}. Error: {}'.format(
                                    param_string, resp.get('errors')[0]['message']))
                            self.error(error_code=9)

                        return
                    snapshot_id = resp['data']['createSnapshot']['id']
                    timestamp_id = resp['data']['createSnapshot']['timestampId']

                name = plant['fullName']
                index = plant['index']
                sample_group = plant['sampleGroup']['name']
                experiment = plant['sampleGroup']['experiment']['name']
                # TODO add seperate step/state to retrieve data and set plant properties
                self.plant.experiment_name = experiment
                self.plant.sample_group_name = sample_group
                self.plant.name = name
                self.plant.index = index
                self.plant.snapshot_id = snapshot_id
                self.plant.timestamp_id = timestamp_id

            except UnableToAuthenticateError:
                self.error(error_code=7)
            except ServerConnectionError as e:
                self._logger.error(e.message)
                self.error(error_code=11)
        else:
            self.error(error_code=1)
            return
        self.rotate()

    def on_enter_drive(self, event):
        print(Fore.BLUE + 'Driving')
        # time.sleep(1)
        self.motor_controller.move_to_position(self.plant.get_picture_count())

    def after_rotate(self, event):
        time.sleep(1)
        self.picture()

    def on_enter_take_picture(self, event):
        print(Fore.BLUE + 'Taking picture at angle ' + str(self.motor_controller.current_angle))
        try:
            picture_path = self.camera_controller.capture_and_download(str(uuid.uuid4()))
            if picture_path is None:
                self.error(error_code=6)
            else:
                self.plant.add_picture(picture_path, self.motor_controller.current_angle)
                self.next_picture()
        except CaptureError:
            self.error(error_code=4)

    def enough_pictures(self, event):
        return self.plant.get_picture_count() >= self.photo_count

    def after_picture(self, event):
        pass

    def on_enter_upload(self, event):
        print(Fore.BLUE + 'Dispatching picture tasks')
        self.image_handler.add_plant(self.plant)

    # TODO rename to after_upload_dispatched
    def after_upload(self, event):
        self.upload_finished()

    def on_enter_error(self, event):
        print(Fore.RED + 'Something wrong happened')
        error_code = event.kwargs.get('error_code', -1)
        # Reset state variables
        self.pic_count = 0
        self.code_information = None
        if self.plant is not None:
            self.plant.delete_all_pictures()
        self.plant = None

        msg = self.error_messages.get(error_code, "Unknown error")
        self._logger.info('Machine transitioned to error state with code {}. ({})'.format(error_code, msg))
        print(Fore.RED + msg)
        self.led_controller.clear_all()
        if error_code == 1:
            self.led_controller.switch_orange(True)
        elif error_code == 2 or error_code == 6 or error_code == 7 or error_code == 9 or error_code == 11:
            self.led_controller.switch_red(True)
        elif error_code == 3:
            self.led_controller.blink_orange()
            self.led_controller.blink_blue()
        elif error_code == 4 or error_code == 5 or error_code == 8:
            self.led_controller.blink_orange()
        elif error_code == 10:
            self.led_controller.blink_blue()

    def on_exit_error(self, event):
        self.led_controller.clear_all()
