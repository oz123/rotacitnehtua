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
from hashlib import sha256
from gettext import  gettext as _
from gi.repository import GObject

from Authenticator.models import Clipboard, Database, Keyring, Logger, OTP, Provider


class Account(GObject.GObject):
    __gsignals__ = {
        'otp_out_of_date': (GObject.SignalFlags.RUN_LAST, None, ()),
        'otp_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    _provider = None

    def __init__(self, _id, username, token_id, provider):
        GObject.GObject.__init__(self)
        self.id = _id
        self.username = username
        self.provider = provider
        self._token_id = token_id
        token = Keyring.get_default().get_by_id(self._token_id)
        self.connect("otp_out_of_date", self._on_otp_out_of_date)
        if token:
            self.otp = OTP(token)
            self._code_generated = True
        else:
            self.otp = None
            self._code_generated = False
            Logger.error("Could not read the secret code,"
                         "the keyring keys were reset manually")

    @staticmethod
    def create(username, token, provider):
        """
        Create a new Account.
        :param username: the account's username
        :param provider: the account's provider
        :param token: the OTP secret token
        :return: Account object
        """
        # Encrypt the token to create a secret_id
        token_id = sha256(token.encode('utf-8')).hexdigest()
        # Save the account
        obj = Database.get_default().insert_account(username, token_id, provider)
        Keyring.get_default().insert(token_id, provider, username, token)
        return Account(obj.id, username, token_id, provider)

    @staticmethod
    def create_from_json(json_obj):
        tags = json_obj["tags"]
        if not tags:
            provider = _("Default")
        else:
            provider = tags[0]
        provider = Provider.get_by_name(provider)
        if not provider:
            provider = Provider.create(name, None, None, None)
        return Account.create(json_obj["label"], json_obj["secret"], provider.provider_id)

    @staticmethod
    def get_by_id(id_):
        obj = Database.get_default().account_by_id(id_)
        return Account(obj.id, obj.username, obj.token_id, obj.provider)

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, provider):
        if isinstance(provider, int):
            self._provider = Provider.get_by_id(provider)
        else:
            self._provider = provider

    def update(self, username, provider):
        """
        Update the account name and/or provider.
        :param username: the account's username
        :param provider: the account's provider
        """
        self.username = username
        self.provider = provider
        account = {
            "username": username,
            "provider": provider.provider_id,
        }
        Database.get_default().update_account(account, self.id)

    def remove(self):
        """
        Remove the account.
        """
        Database.get_default().delete_account(self.id)
        Keyring.get_default().remove(self._token_id)
        self.emit("removed")
        Logger.debug("Account '{}' with id {} was removed".format(self.username,
                                                                  self.id))

    def copy_pin(self):
        """Copy the OTP to the clipboard."""
        Clipboard.set(self.otp.pin)

    def _on_otp_out_of_date(self, *_):
        if self._code_generated:
            self.otp.update()
            self.emit("otp_updated", self.otp.pin)

    def to_json(self):
        token = Keyring.get_default().get_by_id(self._token_id)
        if token:
            return {
                "secret": token,
                "label": self.username,
                "period": 30,
                "digits": 6,
                "type": "OTP",
                "algorithm": "SHA1",
                "thumbnail": "Default",
                "last_used": 0,
                "tags": [self.provider.name]
            }
        return None
