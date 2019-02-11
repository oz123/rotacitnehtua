"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from os import remove, path
from urllib.parse import urlparse, parse_qsl, unquote

from PIL import Image
from pyzbar.pyzbar import decode

from Authenticator.models import Logger, OTP


class QRReader:

    def __init__(self, filename):
        self.filename = filename
        self._codes = None
        self.provider = None
        self.username = None

    def read(self):
        decoded_data = decode(Image.open(self.filename))
        if path.isfile(self.filename):
            remove(self.filename)
        try:
            # See https://github.com/google/google-authenticator/wiki/Key-Uri-Format
            # for a description of the URL format
            url = urlparse(decoded_data[0].data.decode())
            query_params = parse_qsl(url.query)
            self._codes = dict(query_params)

            label = unquote(url.path.lstrip("/"))
            if ":" in label:
                self.provider, self.username = label.split(":", maxsplit=1)
            else:
                self.provider = label
            # provider information could also be in the query params
            self.provider = self._codes.get("issuer", self.provider)

            return self._codes.get("secret")
        except (KeyError, IndexError):
            Logger.error("Invalid QR image")
            return None

    def is_valid(self):
        """
            Validate if the QR code is a valid tfa
        """
        if isinstance(self._codes, dict):
            return OTP.is_valid(self._codes.get("secret"))
        return False
