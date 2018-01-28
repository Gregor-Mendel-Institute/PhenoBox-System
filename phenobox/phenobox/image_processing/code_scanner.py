import logging
import os
import zbar

from PIL import Image


class CodeScanner:
    scanner = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def initialize(self):
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')

    def scan_image(self, path):
        """
        Analyzes the image located by path and tries to extract the code information

        :param path: Path to the image that should be analyzed

        :return: The code Information returned by the zBar image scanner, or None if no code was found
        """
        if not os.path.isfile(path):
            return None
        # obtain image data
        pil = Image.open(path).convert('L')
        width, height = pil.size
        raw = pil.tobytes()

        # wrap image data
        image = zbar.Image(width, height, 'Y800', raw)

        self.scanner.scan(image)

        # Retrieve result( There should be only one qrcode so just take the first one)
        try:
            symbol = next(iter(image.symbols))
        except StopIteration:
            symbol = None  # No code found

        # clean up
        del image

        return symbol
