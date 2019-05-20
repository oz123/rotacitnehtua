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
    ID = "com.github.bilelmoussaoui.Authenticator"
    PasswordID = "com.github.bilelmoussaoui.Authenticator.Login"
    PasswordState = "com.github.bilelmoussaoui.Authenticator.State"
    instance = None

    can_be_locked = GObject.Property(type=bool, default=False)

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
                                                 {
                                                    "password": Secret.SchemaAttributeType.STRING
                                                 })
        self.password_state_schema = Secret.Schema.new(Keyring.PasswordState,
                                                       Secret.SchemaFlags.NONE,
                                                       {
                                                           "state": Secret.SchemaAttributeType.STRING
                                                       })


    @staticmethod
    def get_default():
        if Keyring.instance is None:
            Keyring.instance = Keyring()
        return Keyring.instance

    @staticmethod
    def get_by_id(secret_id):
        """
        Return the OTP token based on a secret ID.

        :param secret_id: the secret ID associated to an OTP token
        :type secret_id: str
        :return: the secret OTP token.
        """
        schema = Keyring.get_default().schema
        password = Secret.password_lookup_sync(
            schema, {"id": str(secret_id)}, None)
        return password

    @staticmethod
    def insert(secret_id, provider, username, token):
        """
        Save a secret OTP token.

        :param secret_id: The secret ID associated to the OTP token
        :param provider: the provider name
        :param username: the username
        :param token: the secret OTP token.


        """
        schema = Keyring.get_default().schema

        data = {
            "id": str(secret_id),
            "name": str(username),
        }
        Secret.password_store_sync(
            schema,
            data,
            Secret.COLLECTION_DEFAULT,
            "{provider} OTP ({username})".format(
                provider=provider, username=username),
            token,
            None
        )

    @staticmethod
    def remove(secret_id):
        """
        Remove a specific secret OTP token.

        :param secret_id: the secret ID associated to the OTP token
        :return bool: Either the token was removed successfully or not
        """
        schema = Keyring.get_default().schema
        success = Secret.password_clear_sync(
            schema, {"id": str(secret_id)}, None)
        return success

    @staticmethod
    def clear():
        """
           Clear all existing accounts.

           :return bool: Either the token was removed successfully or not
       """
        schema = Keyring.get_default().schema
        success = Secret.password_clear_sync(schema, {}, None)
        return success

    @staticmethod
    def get_password():
        schema = Keyring.get_default().password_schema
        password = Secret.password_lookup_sync(schema, {}, None)
        return password

    @staticmethod
    def set_password(password):
        schema = Keyring.get_default().password_schema
        # Clear old password
        Keyring.remove_password()
        # Store the new one
        Secret.password_store_sync(
            schema,
            {},
            Secret.COLLECTION_DEFAULT,
            "Authenticator password",
            password,
            None
        )
        Keyring.set_password_state(True)

    @staticmethod
    def is_password_enabled():
        schema = Keyring.get_default().password_state_schema
        state = Secret.password_lookup_sync(schema, {}, None)
        return state == 'true' if state else False

    @staticmethod
    def set_password_state(state):
        keyring = Keyring.get_default()
        schema = keyring.password_state_schema
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
        keyring.props.can_be_locked = state and keyring.has_password()


    @staticmethod
    def has_password():
        return Keyring.get_password() is not None

    @staticmethod
    def remove_password():
        schema = Keyring.get_default().password_schema
        Secret.password_clear_sync(schema, {}, None)
        Keyring.set_password_state(False)
