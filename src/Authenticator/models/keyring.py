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
from gi.repository import GObject, Secret


class Keyring(GObject.GObject):
    ID: str = "com.github.bilelmoussaoui.Authenticator"
    PasswordID: str = "com.github.bilelmoussaoui.Authenticator.Login"
    PasswordState: str = "com.github.bilelmoussaoui.Authenticator.State"
    instance: 'Keyring' = None

    can_be_locked: GObject.Property = GObject.Property(type=bool, default=False)

    def __init__(self):
        GObject.GObject.__init__(self)
        self.schema = Secret.Schema.new(Keyring.ID,
                                        Secret.SchemaFlags.NONE,
                                        {
                                            "id": Secret.SchemaAttributeType.STRING,
                                            "name": Secret.SchemaAttributeType.STRING,
                                        })
        self.password_schema = Secret.Schema.new(Keyring.PasswordID,
                                                 Secret.SchemaFlags.NONE,
                                                 {"password": Secret.SchemaAttributeType.STRING})
        self.password_state_schema = Secret.Schema.new(Keyring.PasswordState,
                                                       Secret.SchemaFlags.NONE,
                                                       {"state": Secret.SchemaAttributeType.STRING})
        self.props.can_be_locked = self.is_password_enabled() and self.has_password()

    @staticmethod
    def get_default():
        if Keyring.instance is None:
            Keyring.instance = Keyring()
        return Keyring.instance

    def get_by_id(self, token_id: str) -> str:
        """
        Return the OTP token based on a secret ID.

        :param token_id: the secret ID associated to an OTP token
        :type token_id: str
        :return: the secret OTP token.
        """
        schema = self.schema
        token = Secret.password_lookup_sync(schema, {"id": str(token_id)},
                                            None)
        return token

    def insert(self, token_id: str, provider: str, username: str, token: str):
        """
        Save a secret OTP token.

        :param token_id: The secret ID associated to the OTP token
        :param provider: the provider name
        :param username: the username
        :param token: the secret OTP token.


        """
        schema = self.schema

        data = {
            "id": str(token_id),
            "name": str(username),
        }
        Secret.password_store_sync(
            schema,
            data,
            Secret.COLLECTION_DEFAULT,
            "{provider} OTP ({username})".format(provider=provider,
                                                 username=username),
            token,
            None
        )

    def remove(self, token_id: str) -> bool:
        """
        Remove a specific secret OTP token.

        :param secret_id: the secret ID associated to the OTP token
        :return bool: Either the token was removed successfully or not
        """
        schema = self.schema
        success = Secret.password_clear_sync(schema, {"id": str(token_id)},
                                             None)
        return success

    def clear(self) -> bool:
        """
           Clear all existing accounts.

           :return bool: Either the token was removed successfully or not
       """
        schema = self.schema
        success = Secret.password_clear_sync(schema, {}, None)
        return success

    def get_password(self) -> str:
        schema = self.password_schema
        password = Secret.password_lookup_sync(schema, {}, None)
        return password

    def set_password(self, password: str):
        schema = self.password_schema
        # Clear old password
        self.remove_password()
        # Store the new one
        Secret.password_store_sync(
            schema,
            {},
            Secret.COLLECTION_DEFAULT,
            "Authenticator password",
            password,
            None
        )
        self.set_password_state(True)

    def is_password_enabled(self) -> bool:
        schema = self.password_state_schema
        state = Secret.password_lookup_sync(schema, {}, None)
        return state == 'true' if state else False

    def set_password_state(self, state: bool):
        schema = self.password_state_schema
        if not state:
            Secret.password_clear_sync(schema, {}, None)
        else:
            Secret.password_store_sync(
                schema,
                {},
                Secret.COLLECTION_DEFAULT,
                "Authenticator state",
                "true",
                None
            )
        self.props.can_be_locked = state and self.has_password()

    def has_password(self) -> bool:
        return self.get_password() is not None

    def remove_password(self):
        schema = self.password_schema
        Secret.password_clear_sync(schema, {}, None)
        self.set_password_state(False)
