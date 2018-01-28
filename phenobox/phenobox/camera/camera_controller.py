import ctypes
import errno
import logging
import os

from camera.errors import ConnectionError, CaptureError
from config import config


class libgphoto2error(Exception):
    def __init__(self, result, message):
        self.result = result
        self.message = message

    def __str__(self):
        return self.message + ' (' + str(self.result) + ')'


class CameraFilePath(ctypes.Structure):
    _fields_ = [('name', (ctypes.c_char * 128)),
                ('folder', (ctypes.c_char * 1024))]


# gphoto constants
# Defined in 'gphoto2-port-result.h'
GP_OK = 0
GP_ERROR = -1  # generic error
GP_ERROR_BAD_PARAMETERS = -2  # bad parameters passed
GP_ERROR_NO_MEMORY = -3  # out of memory
GP_ERROR_LIBRARY = -4  # error in camera driver
GP_ERROR_UNKNOWN_PORT = -5  # unknown libgphoto2 port passed
GP_ERROR_NOT_SUPPORTED = -6  # whatever you tried isn't supported
GP_ERROR_IO = -7  # Generic I/O error - there's a surprise
GP_ERROR_FIXED_LIMIT_EXCEEDED = -8  # internal buffer overflow
GP_ERROR_TIMEOUT = -10  # timeout - no prizes for guessing that one
GP_ERROR_IO_SUPPORTED_SERIAL = -20  # Serial port not supported
GP_ERROR_IO_SUPPORTED_USB = -21  # USB ports not supported
GP_ERROR_IO_INIT = -31  # Unable to init I/O
GP_ERROR_IO_READ = -34  # I/O Error during read
GP_ERROR_IO_WRITE = -35  # I/O Error during write
GP_ERROR_IO_UPDATE = -37  # I/O during update of settings
GP_ERROR_IO_SERIAL_SPEED = -41  # Serial speed not possible
GP_ERROR_IO_USB_CLEAR_HALT = -51  # Error
# CameraCaptureType enum in 'gphoto2-camera.h'
GP_CAPTURE_IMAGE = 0
# CameraFileType enum in 'gphoto2-file.h'
GP_FILE_TYPE_NORMAL = 1

PTR = ctypes.pointer

# FIXME this crashes sphinx documentation try to move into class CameraController
gp = ctypes.CDLL('libgphoto2.so')
#gp=None

def check(result):
    """
    Utility function to check the return value of libgphoto2 function calls and raise an error if appropriate

    :param result: the result returned by the libgphoto2 function call

    :raises libgphoto2error: if the result value represents an error value

    :return: the given result parameter
    """
    if result < 0:
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise libgphoto2error(result, message)
    return result


def check_unref(result, camfile):
    if result != 0:
        gp.gp_file_unref(camfile._cf)
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise libgphoto2error(result, message)


class CameraController:
    context = None

    cam = None  #:a reference to the camera which should be used

    class cameraFile(object):
        """
        Class used to represent a file on the camera. Exposes utility functions to access the file
        """

        def __init__(self, cam=None, context=None, srcfolder=None, srcfilename=None):
            self._cf = ctypes.c_void_p()
            check(gp.gp_file_new(PTR(self._cf)))
            if cam:
                check_unref(gp.gp_camera_file_get(cam, srcfolder, srcfilename, GP_FILE_TYPE_NORMAL, self._cf, context),
                            self)

        def open(self, filename):
            check(gp.gp_file_open(PTR(self._cf), filename))

        def save(self, filename=None):
            if filename is None: filename = self.name
            check(gp.gp_file_save(self._cf, filename))

        def ref(self):
            check(gp.gp_file_ref(self._cf))

        def unref(self):
            check(gp.gp_file_unref(self._cf))

        def clean(self):
            check(gp.gp_file_clean(self._cf))

        def copy(self, source):
            check(gp.gp_file_copy(self._cf, source._cf))

        def __dealoc__(self, filename):
            check(gp.gp_file_free(self._cf))

        def _get_name(self):
            name = ctypes.c_char_p()
            check(gp.gp_file_get_name(self._cf, PTR(name)))
            return name.value

        def _set_name(self, name):
            check(gp.gp_file_set_name(self._cf, str(name)))

        name = property(_get_name, _set_name)

    def __init__(self, target_dir=None):
        if target_dir is None:
            self.target_dir = getattr(config, 'cfg').get('box', 'local_image_folder')
        else:
            self.target_dir = target_dir
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.info('Target directory set to {}'.format(self.target_dir))

    def connect(self):
        """
        Connects to the attached camera

        :raises ConnectionError: if the connection to the camera failed

        :return: None
        """
        if self.cam is None:
            self.cam = ctypes.c_void_p()
            gp.gp_camera_new(ctypes.byref(self.cam))
            retval = gp.gp_camera_init(self.cam, self.context)
            if retval != GP_OK:
                self.release()
                self._logger.warning('Unable to connect to camera. (Error code: {})'.format(retval))
                raise ConnectionError('Unable to connect to camera')

    def release(self):
        """
        Disconnects from the camera

        :return: None
        """
        if self.cam is not None:
            gp.gp_camera_exit(self.cam, self.context)
            gp.gp_camera_unref(self.cam)
            self.cam = None

    def initialize(self):
        """
        Sets up the context needed by gphoto

        :return: None
        """
        self.context = gp.gp_context_new()

    def capture_and_download(self, name):
        """
        Takes a photo and downloads it from the camera and saves it to the target_dir

        :param name: the file name which should be used when saving the downloaded image

        :return: The return value of :meth:`.download`
        """
        self.connect()
        file_path = CameraFilePath()
        retval = gp.gp_camera_capture(self.cam, GP_CAPTURE_IMAGE, PTR(file_path), self.context)
        if retval != GP_OK:
            self._logger.warning('Error during capture. (Error code: {})'.format(retval))
            self.release()
            raise CaptureError("Unable to capture")
        else:
            return self.download(os.path.join(self.target_dir), file_path, name)

    def download(self, dest_folder, file_path, name):
        """
        Downloads the image given by file_path and saves it to the path given by dest_folder with the given name

        :param dest_folder: The directory to store the image to
        :param file_path: The path to the image on the camera
        :param name: The file name to be used for the downloaded image

        :return: the full path to the downloaded image or None if the download was not successfull
        """
        dest = os.path.join(dest_folder, name + '.jpg')

        try:
            os.makedirs(dest[:dest.rindex('/') + 1])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self._logger.exception('Unable to create folder ({}). (errno: {})'.format(dest, exception.errno))
                return None
                # raise  # TODO handle this
        try:
            cfile = self.cameraFile(self.cam, self.context, file_path.folder, file_path.name)
            cfile.save(dest)
            gp.gp_file_unref(cfile._cf)
        except libgphoto2error as err:
            self._logger.exception('Unable to download and save image from camera')
            return None
        return dest

    # TODO refactor into property
    def get_target_dir(self):
        return self.target_dir

    def close(self):
        """
        Alias for :meth:`.release`

        :return: None
        """
        self.release()
