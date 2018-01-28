import datetime
import jsonpickle
import logging
import os
from __builtin__ import len


class Plant:
    def __init__(self):
        # TODO add full_name
        self.name = ""
        self.index = 0
        self.experiment_name = ""
        self.sample_group_name = ""
        self.snapshot_id = ""
        self.timestamp_id = ""
        self.pictures = []
        self.date = datetime.datetime.now()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def add_picture(self, path, angle):
        """
        Append a new picture with the full path and the angle at which it was taken to the list of pictures
        :param path: The absolute path to the image
        :param angle: The angle at which the image was taken
        :return:
        """
        self.pictures.append((path, angle))

    def delete_picture(self, index):
        """
        Removes the entry from the list of pictures and deletes the image from the filesystem

        :param index: The index of the image in the list

        :return: None
        """
        if index < len(self.pictures):
            pic_path, _ = self.pictures[index]
            os.remove(pic_path)
            self.pictures.pop(index)

    def delete_all_pictures(self):
        """
        Deletes all pictures for this plant from the filesystem

        :return: None
        """
        for i in range(len(self.pictures) - 1, -1, -1):
            self.delete_picture(i)

    def get_picture_count(self):
        # TODO change to property
        return len(self.pictures)

    def get_first_picture(self):
        """
        Returns a tuple containing the absolute path to the first image and the angle at which it was taken

        :return: A tuple containing of the absolute image path and the angle (path, angle)
        """
        return self.pictures[0] if len(self.pictures) > 0 else None

    def get_pictures(self):
        """
        Gets the list of all pictures.
        :return: A list containing tuples of the absolute image path and the angle at which they were taken (path, angle)
        """
        return self.pictures

    def forget(self, target_dir):
        """
        Remove the file which was used to persist the plant information

        :param target_dir: The directory in which the file is stored

        :return: None
        """
        file_path = os.path.join(target_dir, self.name + '.json')
        if os.path.exists(file_path):
            os.remove(file_path)

    def persist(self, target_dir):
        """
        Store the plant information as a json file to the given directory for later retrieval

        :param target_dir: The directory to which the file should be saved

        :return: None
        """
        self._logger.info('Persisting plant {} to {}'.format(self.name, target_dir))
        json = jsonpickle.encode(self)
        dest = os.path.join(target_dir, self.name + '.json')
        with open(dest, "w") as json_file:
            json_file.write(json)
            json_file.close()
            # TODO error handling

    @staticmethod
    def load(path):
        """
        Loads the instance from the json file given by path

        :param path: The absolute path to the json file in which the instance information has been stored

        :return: The corresponding Plant instance
        """
        with open(path) as json_file:
            json_str = json_file.read()
            obj = jsonpickle.decode(json_str)
            obj._logger = logging.getLogger(__name__)
            obj._logger.setLevel(logging.INFO)
            return obj
