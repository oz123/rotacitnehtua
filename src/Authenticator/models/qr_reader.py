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

    @staticmethod
    def from_file(filename: str):
        decoded_data = decode(Image.open(filename))
        if path.isfile(filename):
            remove(filename)
        try:
            # See https://github.com/google/google-authenticator/wiki/Key-Uri-Format
            # for a description of the URL format
            url = urlparse(decoded_data[0].data.decode())
            query_params = parse_qsl(url.query)
            url_data = dict(query_params)

            username = None
            label = unquote(url.path.lstrip("/"))
            if ":" in label:
                provider, username = label.split(":", maxsplit=1)
            else:
                provider = label
            # provider information could also be in the query params
            provider = url_data.get("issuer", provider)

            token = url_data.get("secret")
            assert OTP.is_valid(token)

            return {
                'username': username,
                'provider': provider,
                'token': token
            }
        except (KeyError, IndexError):
            Logger.error("Invalid QR image")
