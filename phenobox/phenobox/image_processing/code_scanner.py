import logging
import os

from PIL import Image
from pyzbar import pyzbar
from pyzbar.wrapper import ZBarSymbol


class CodeScanner:

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self.approximate_area = None

    def scan_image(self, path):
        """
        Analyzes the image located by path and tries to extract the code information

        :param path: Path to the image that should be analyzed

        :return: The code Information returned by the zBar image scanner, or None if no code was found
        """
        if not os.path.isfile(path):
            return None
        im = Image.open(path)

        width, height = im.size

        w_s = width * 0.4
        h_s = height * 0.4

        reduced_size = int(w_s), int(h_s)
        im = im.resize(reduced_size)

        if self.approximate_area:
            im_c = im.crop(self.approximate_area)
            res = pyzbar.decode(im_c, symbols=[ZBarSymbol.QRCODE])
            if len(res) == 0:
                self.approximate_area = None
            else:
                return res[0].data

        res = pyzbar.decode(im, symbols=[ZBarSymbol.QRCODE])

        if len(res) > 0:
            rect = res[0].rect
            offset_width = rect.width * 1.5
            offset_height = rect.height * 1.5
            self.approximate_area = (
                rect.left - offset_width,
                rect.top - offset_height,
                rect.left + offset_width,
                rect.top + offset_height
            )
            return res[0].data
        return None
