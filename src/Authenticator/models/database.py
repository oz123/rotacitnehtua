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

 You  ould have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3
from os import path, makedirs
from gi.repository import GLib
from collections import namedtuple
from shutil import move
from typing import Iterable

from Authenticator.models import Logger


Provider = namedtuple('Provider', ['id', 'name', 'website', 'doc_url', 'image'])
Account = namedtuple('Account', ['id', 'username', 'token_id', 'provider'])


class Database:
    """SQL database handler."""

    # Default instance
    instance = None
    # Database version number
    db_version: int = 7

    def __init__(self):
        self.migrations_dir = path.join(path.dirname(__file__), '../migrations')
        database_created = self.__create_database_file()
        if database_created:
            self.__apply_migrations()
        self.conn = sqlite3.connect(self.db_file)

    @staticmethod
    def get_default():
        """Return the default instance of database"""
        if Database.instance is None:
            Database.instance = Database()
        return Database.instance

    @property
    def db_dir(self) -> str:
        return path.join(GLib.get_user_config_dir(),
                         'Authenticator')

    @property
    def db_file(self) -> str:
        return path.join(self.db_dir,
                         'database-{}.db'.format(str(Database.db_version))
                         )

    def insert_account(self, username: str, token_id: str, provider: str):
        """
        Insert a new account to the database
        :param username: Account name
        :param token_id: The token identifier stored using libsecret
        :param provider: The provider foreign key
        """
        query = "INSERT INTO accounts (username, token_id, provider) VALUES (?, ?, ?)"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, [username, token_id, provider])
            self.conn.commit()
            return Account(cursor.lastrowid, username, token_id, provider)
        except Exception as error:
            Logger.error("[SQL] Couldn't add a new account")
            Logger.error(str(error))

    def insert_provider(self, name: str, website: str,
                        doc_url: str = None, image: str = None):
        """
        Insert a new provider to the database
        :param name: The provider name
        :param website: The provider website, used to extract favicon
        :param doc_url: The provider doc_url, used to allow user get the docs
        :param image: The image path of a provider
        """
        query = "INSERT INTO providers (name, website, doc_url, image) VALUES (?, ?, ?, ?)"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, [name, website, doc_url, image])
            self.conn.commit()
            return Provider(cursor.lastrowid, name, website, doc_url, image)
        except Exception as error:
            Logger.error("[SQL] Couldn't add a new account")
            Logger.error(str(error))

    def account_by_id(self, id_: int) -> Account:
        """
            Get an account by the ID
            :param id_: int the account id
            :return: Account: The account data
        """
        query = "SELECT * FROM accounts WHERE id=?"
        try:
            data = self.conn.cursor().execute(query, (id_,))
            return Account(*data.fetchone())
        except Exception as error:
            Logger.error("[SQL] Couldn't get account with ID={}".format(id_))
            Logger.error(str(error))
        return None

    def accounts_by_provider(self, provider_id: int) -> Iterable[Account]:
        query = "SElECT * FROM accounts WHERE provider=?"
        query_d = self.conn.execute(query, (provider_id, ))
        accounts = query_d.fetchall()
        return [Account(*account) for account in accounts]

    def provider_by_id(self, id_: int) -> Provider:
        """
            Get a provider by the ID
            :param id_: int the provider id
            :return: Provider: The provider data
        """
        query = "SELECT * FROM providers WHERE id=?"
        try:
            data = self.conn.cursor().execute(query, (id_,))
            return Provider(*data.fetchone())
        except Exception as error:
            Logger.error("[SQL] Couldn't get provider with ID={}".format(id_))
            Logger.error(str(error))
        return None

    def provider_by_name(self, provider_name: str) -> Provider:
        """
            Get a provider by the ID
            :param id_: int the provider id
            :return: Provider: The provider data
        """
        query = "SELECT * FROM providers WHERE name LIKE ? "
        try:
            data = self.conn.cursor().execute(query, (provider_name,))
            provider = data.fetchone()
            return Provider(*provider) if provider else None
        except Exception as error:
            Logger.error("[SQL] Couldn't get provider with name={}".format(provider_name))
            Logger.error(str(error))
        return None

    def delete_account(self, id_: int):
        """
            Remove an account by ID.

            :param id_: the account ID
            :type id_: int
        """
        self.__delete("accounts", id_)

    def delete_provider(self, id_: int):
        """
            Remove a provider by ID.

            :param id_: the provider ID
            :type id_: int
        """
        self.__delete("providers", id_)

    def update_account(self, account_data: dict, id_: int):
        """
        Update an account by id
        """
        self.__update_by_id("accounts", account_data, id_)

    def update_provider(self, provider_data: dict, id_: int):
        # Update a provider by id
        self.__update_by_id("providers", provider_data, id_)

    def search_accounts(self, terms: Iterable[str]) -> Iterable[Account]:
        if terms:
            filters = " ".join(terms)
            if filters:
                filters = "%" + filters + "%"
            query = """
                        SELECT A.* FROM accounts A
                        JOIN providers P
                        ON A.provider = P.id
                        WHERE
                        A.username LIKE ?
                        OR
                        P.name LIKE ?
                        GROUP BY provider
                        ORDER BY  A.username ASC
                    """
            try:
                data = self.conn.cursor().execute(query, (filters, filters, ))
                accounts = data.fetchall()
                return [Account(*account) for account in accounts]
            except Exception as error:
                Logger.error("[SQL]: Couldn't search for an account")
                Logger.error(str(error))
        return []

    @property
    def accounts_count(self):
        """
            Count the total number of existing accounts.

           :return: int
        """
        return self.__count("accounts")

    @property
    def providers_count(self):
        """
            Count the total number of existing providers
            :return: int
        """
        return self.__count("providers")

    def get_providers(self, **kwargs) -> Iterable[Provider]:
        only_used = kwargs.get("only_used",)
        query = "SELECT * FROM providers"
        if only_used:
            query += " WHERE id IN (SELECT DISTINCT provider FROM accounts)"
        try:
            data = self.conn.cursor().execute(query)
            providers = data.fetchall()
            return [Provider(*provider) for provider in providers]
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch providers list")
            Logger.error(str(error))
        return None

    @property
    def accounts(self) -> [Account]:
        """
            Retrieve the list of accounts.

            :return list
        """
        query = "SELECT * FROM accounts"
        try:
            data = self.conn.cursor().execute(query)
            accounts = data.fetchall()
            return [Account(*account) for account in accounts]
        except Exception as error:
            Logger.error("[SQL] Couldn't fetch accounts list")
            Logger.error(str(error))
        return None

    def __create_database_file(self):
        """
        Create an empty database file for the first start of the application.
        """
        created = False
        for i in range(3, self.db_version + 1):
            db_file = path.join(self.db_dir, "database-{}.db".format(i))
            if path.exists(db_file):
                move(db_file, self.db_file)
                created = True
                break
        if not created:
            makedirs(path.dirname(self.db_file), exist_ok=True)
            if not path.exists(self.db_file):
                with open(self.db_file, 'w') as file_obj:
                    file_obj.write('')
                created = True
        return created

    def __apply_migrations(self):
        """
        Create the needed tables to run the application.
        """
        from yoyo import read_migrations
        from yoyo import get_backend
        backend = get_backend('sqlite:///' + self.db_file)
        migrations = read_migrations(self.migrations_dir)
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

    def __count(self, table_name: str) -> int:
        query = "SELECT COUNT(id) AS count FROM " + table_name
        try:
            data = self.conn.cursor().execute(query)
            return data.fetchone()[0]
        except Exception as error:
            Logger.error("[SQL]: Couldn't count the results from " + table_name)
            Logger.error(str(error))
        return None

    def __delete(self, table_name: str, id_: int):
        """
            Remove a row by ID.

            :param id_: the row ID
            :type id_: int
        """
        query = "DELETE FROM {} WHERE id=?".format(table_name)
        try:
            self.conn.execute(query, (id_,))
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't remove the row '{}'".format(id_))
            Logger.error(str(error))

    def __update_by_id(self, table_name: str, data: dict, id_: int):
        query = "UPDATE {} SET ".format(table_name)
        resources = []
        i = 0
        for table_column, value in data.items():
            query += " {}=?".format(table_column)
            if i != len(data) - 1:
                query += ","
            resources.append(value)
            i += 1
        resources.append(id_)
        query += "WHERE id=?"
        try:
            self.conn.execute(query, resources)
            self.conn.commit()
        except Exception as error:
            Logger.error("[SQL] Couldn't update row by id")
            Logger.error(error)
