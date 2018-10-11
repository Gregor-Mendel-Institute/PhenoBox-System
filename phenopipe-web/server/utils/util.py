import operator
import os
from functools import reduce

from dateutil import tz

from server.modules.processing.exceptions import NoPathMappingFoundError


def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)


def get_local_path_from_smb(smb_url, path_map):
    """
    Takes in a SMB URL to a shared folder and a dict which contains a mapping of SMB URLs to local mount points

    :param smb_url: The SMB URL which represents the location
    :param path_map: A dict which represents a mapping of SMB URLS to local pahts (mount points)

    :return: The local path which corresponds to the SMB URL
    """
    url, local_path = next(((smb, path) for smb, path in path_map.items() if smb_url.startswith(smb)), (None, None))
    if local_path is not None:
        return os.path.join(local_path, remove_prefix(smb_url, url))
    raise NoPathMappingFoundError(url, 'No local path was found for the given URL')


def remove_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def utc_to_local(utc):
    """
    Converts the given UTC timestamp to the local timezone

    :param utc: UTC timestamp

    :return: Localized UTC timestamp
    """
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def as_string(value):
    if value is None:
        return None
    elif isinstance(value, str):
        return value.decode('utf-8')
    elif isinstance(value, unicode):
        return value


def static_vars(**kwargs):
    """
    Decorator to attach and initialize static variables to functions

    :param kwargs: Name value pairs of variables and their values

    """

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate
