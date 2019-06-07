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
import json
from gi.repository import Gio

from Authenticator.models import Account, AccountsManager, Logger
from Authenticator.widgets import AccountsWidget


class Backup:

    def __init__(self):
        pass

    @staticmethod
    def import_accounts(accounts: [dict]):
        accounts_widget = AccountsWidget.get_default()
        accounts_manager = AccountsManager.get_default()
        for account in accounts:
            try:
                new_account = Account.create_from_json(account)
                accounts_manager.add(new_account.provider, new_account)
                accounts_widget.append(new_account)
            except Exception as e:
                Logger.error("[Restore] Failed to import accounts")
                Logger.error(str(e))

    @staticmethod
    def export_accounts() -> [dict]:
        accounts = AccountsManager.get_default().accounts
        exported_accounts = []
        for account in accounts:
            json_account = account.to_json()
            exported_accounts.append(json_account)
        return exported_accounts


class BackupJSON:

    def __init__(self):
        pass

    @staticmethod
    def export_file(uri: str):
        accounts = Backup.export_accounts()
        gfile = Gio.File.new_for_uri(uri)
        stream = gfile.replace(None,
                               False,
                               Gio.FileCreateFlags.REPLACE_DESTINATION,
                               None)
        data_stream = Gio.DataOutputStream.new(stream)
        data_stream.put_string(json.dumps(accounts), None)
        stream.close()

    @staticmethod
    def import_file(uri: str):
        gfile = Gio.File.new_for_uri(uri)
        accounts = gfile.load_contents()[1].decode("utf-8")
        Backup.import_accounts(json.loads(accounts))
