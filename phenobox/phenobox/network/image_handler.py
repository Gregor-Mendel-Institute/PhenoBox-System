import errno
import fnmatch
import logging
import os
import threading
from Queue import Queue, Empty

from PIL import Image
from colorama import Fore
from requests import Session, ConnectionError

from config import config
from network import ServerUnableToSaveImageError
from network import UnableToAuthenticateError
from plant import Plant


class ImageHandler(threading.Thread):
    """
    Background thread to handle image conversion and upload to the network share
    """

    def __init__(self, auth, local_dir=None, persist_dir=None, target_dir=None, photo_count=6):
        super(ImageHandler, self).__init__()
        self._stop = threading.Event()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._photo_count = photo_count
        self._auth = auth
        self._graphql_address = '{}{}'.format(getattr(config, 'cfg').get('server', 'base_address'),
                                              getattr(config, 'cfg').get('server', 'graphql_endpoint'))
        #: A queue which holds all the plant instances which need to be processed
        self.queue = Queue()
        if local_dir is None:
            self.source_path = getattr(config, 'cfg').get('box', 'local_image_folder')
        else:
            self.source_path = local_dir

        if persist_dir is None:
            self.persist_dir = os.path.join(self.source_path, 'persisted')  # TODO use config value
        else:
            self.persist_dir = persist_dir

        if target_dir is None:
            self.target_path = getattr(config, 'cfg').get('box', 'shared_folder_mountpoint')
        else:
            self.target_path = target_dir

        try:
            os.makedirs(self.source_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        try:
            os.makedirs(self.persist_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def stop(self):
        """
        Signals the thread that it should shut itself down gracefully

        :return: None
        """
        self._stop.set()

    def stopped(self):
        """
        Inidicates whether the thread should shut itself down

        :return: True if the thread should be stopped, False otherwise
        """
        return self._stop.isSet()

    def read_from_disk(self, basepath):
        """
        Loads all persisted entries from the filesystem and enqueues them to continue uploading

        :param basepath: The path where all persisted plant files are located

        :return: None
        """
        for entry in os.listdir(basepath):
            if os.path.isfile(os.path.join(basepath, entry)) and fnmatch.fnmatch(entry, '*.json'):
                self._logger.info('Loading {} from disk for processing'.format(entry))
                plant = Plant.load(os.path.join(basepath, entry))
                self.add_plant(plant)
                # os.remove(os.path.join(basepath, entry))

    def add_plant(self, plant):
        """
        Enqueue the plant instance to be processed

        :param plant: The plant instance to be enqueued

        :return: None
        """
        self.queue.put(plant)

    def _get_img(self, path):
        """
        Utility method to get an appropriately sized Image instance from the given path

        :param path: The full path to the image file

        :return: A pillow.Image instance
        """
        img = Image.open(path)

        img = img.rotate(90, expand=True)
        width, height = img.size
        return img.resize((int(width / 6.5), int(height / 6.5)), Image.ANTIALIAS)

    def _notify_server(self, path, snapshot_id, filename, angle):
        """
        Utility method to create image entries on the server.

        :param path: The path to the image folder relative to the NFS mount point
        :param snapshot_id: The snapshot ID this image belongs to
        :param filename: The name of the image
        :param angle: The angle at which the image was taken

        :raises ServerUnableToSaveImageError: if the server returns a negative response because it was not able to
            create the according entries
        :return: None
        """
        target_path = '{}/{}'.format(getattr(config, 'cfg').get('server', 'shared_folder_url'),
                                     path)
        param_string = 'snapshotId: "{}", path:"{}", filename:"{}",angle:{}'.format(snapshot_id,
                                                                                    target_path,
                                                                                    filename,
                                                                                    str(angle))
        # TODO check if possible to create session outside and pass it in to reuse
        s = Session()

        prepped_req = self._auth.prep_post(self._graphql_address, data={
            'query': 'mutation{addImage(' + param_string + '){ok}}'})
        r = s.send(prepped_req)
        if r.status_code != 200:
            raise ServerUnableToSaveImageError('Unable to create image instance on server. Http status {}')
        resp = r.json()
        if resp.get('errors', None):
            self._logger.error(resp.get('errors')[0]['message'])
            raise ServerUnableToSaveImageError('Unable to create image instance on server. {}'.format(
                resp.get('errors')[0]['message']))

    def run(self):
        """
        Main loop for this worker thread. Loads persisted plant entries from the disk on startup and then takes images
        from the queue for processing.
        If the thread is stopped it will persist all remaining plants to be able to resume work after startup again.

        :return: None
        """
        self.read_from_disk(self.persist_dir)
        # TODO Check if according snapshots exist (Could be deleted in the meantime)
        while not self.stopped():
            try:
                plant = self.queue.get(block=True, timeout=2)

                stored_pictures = list()

                shared_path = os.path.join(plant.experiment_name,
                                           plant.date.strftime("%Y_%m_%d"), str(hash(plant.timestamp_id)))
                dest_dir = os.path.join(self.target_path, shared_path)
                try:
                    os.makedirs(dest_dir)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        self._logger.exception(
                            'Unable to create folder ({}). (errno: {})'.format(dest_dir, exception.errno))
                        print(Fore.RED + 'error during mkdirs')
                        # TODO send notification to admin
                        # TODO bailout?
                        self.add_plant(plant)
                        continue
                        # raise
                pictures = list(plant.pictures)

                for index, picture in enumerate(pictures):
                    if self.stopped():
                        print(Fore.YELLOW + 'Persist current plant')
                        plant.persist(self.persist_dir)
                        break
                    path, angle = picture
                    img = self._get_img(path)
                    filename = '{name}_{angle}.png'.format(
                        name=plant.name.replace(" ", "_"),
                        angle=str(angle))
                    dest = os.path.join(dest_dir, filename)
                    try:
                        img.save(dest, compress_level=9)
                        self._notify_server(shared_path, plant.snapshot_id, filename, angle)
                        stored_pictures.append(dest)
                        print(Fore.YELLOW + 'Saved')
                        # The current plant is always at index 0 because the previous one is deleted before
                        plant.delete_picture(0)
                    except KeyError as e:
                        self._logger.exception('Key Error while saving picture. msg: {}'.format(e.message))
                        print(Fore.RED + e.message)
                        self.add_plant(plant)
                    except IOError as e:
                        self._logger.exception('IO Error while saving picture. msg: {}'.format(e.message))
                        print(Fore.RED + e.message)
                        self.add_plant(plant)
                    except UnableToAuthenticateError as e:
                        os.remove(dest)
                        stored_pictures = stored_pictures[:-1]
                        self._logger.error(e.message)
                        self.add_plant(plant)
                    except ServerUnableToSaveImageError as e:
                        # TODO Inform user or admin
                        print(Fore.RED + e.message)
                        self._logger.error(e.message)
                        self.add_plant(plant)
                    except ConnectionError as e:
                        print(Fore.RED + e.message)
                        self._logger.error(e.message)
                        self.add_plant(plant)
                    if plant.get_picture_count() > 0:
                        print(
                                Fore.YELLOW + str(plant.get_picture_count()) + " images remaining for plant {}".format(
                            plant.name))

                if plant.get_picture_count() == 0:
                    plant.forget(self.persist_dir)

                print(Fore.YELLOW + "Plant {} done".format(plant.name))
                self.queue.task_done()
                print(Fore.YELLOW + str(self.queue.qsize()) + " plants remaining")
            except Empty:
                pass
        print(Fore.YELLOW + "Persist remaining plants ~" + str(self.queue.qsize()))
        while not self.queue.empty():
            try:
                plant = self.queue.get(False)
                plant.persist(self.persist_dir)
                self.queue.task_done()
            except Empty:
                break
        print(Fore.YELLOW + "Image handler stopped")
