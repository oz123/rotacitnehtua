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
from gi.repository import GObject, GLib


class AccountsManager(GObject.GObject):
    __gsignals__ = {
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (int,)),
    }
    instance = None
    empty = GObject.Property(type=bool, default=False)

    # A list that contains a tuple (provider, accounts)
    __accounts = []

    def __init__(self):
        GObject.GObject.__init__(self)
        self._accounts_per_provider = []
        self._alive = True
        self.__fill_accounts()

        self.counter_max = 30
        self.counter = self.counter_max
        GLib.timeout_add_seconds(1, self.__update_counter, None)

    @staticmethod
    def get_default():
        if AccountsManager.instance is None:
            AccountsManager.instance = AccountsManager()
        return AccountsManager.instance

    def add(self, provider, account):
        added = False
        for _provider, accounts in self._accounts_per_provider:
            if provider == _provider:
                accounts.append(account)
                added = True
                break
        if not added:
            self._accounts_per_provider.append((provider, [account]))
        self.props.empty = len(self._accounts_per_provider) == 0

    def delete(self, account):
        provider_index = 0
        _accounts = None
        for provider, accounts in self._accounts_per_provider:
            if account in accounts:
                _accounts = accounts
                break
            provider_index += 1
        if provider:
            _accounts.remove(account)
            if not len(_accounts):
                del self._accounts_per_provider[provider_index]
        self.props.empty = len(self._accounts_per_provider) == 0

    def search(self, terms):
        from .database import Database
        from .account import Account

        accounts = Database.get_default().search_accounts(terms)
        _accounts = []
        for account in accounts:
            account = Account(*account)
            if account.otp:
                _accounts.append(account)
        return _accounts

    @property
    def accounts_per_provider(self):
        return self._accounts_per_provider

    @property
    def accounts(self):
        accounts = []
        for _, _accounts in self._accounts_per_provider:
            accounts.extend(_accounts)
        return accounts

    @property
    def accounts_count(self):
        count = 0
        for _, accounts in self._accounts_per_provider:
            count += len(accounts)
        return count

    def clear(self):
        self._accounts_per_provider = []

    def kill(self):
        self._alive = False

    def update_childes(self, signal, data=None):
        for _, accounts in self._accounts_per_provider:
            for account in accounts:
                if data:
                    account.emit(signal, data)
                else:
                    account.emit(signal)

    def __update_counter(self, *args):
        if self._alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self.update_childes("otp_out_of_date")
            self.emit("counter_updated", self.counter)
            return True
        return False

    def __fill_accounts(self):
        from .database import Database
        from .account import Account
        from .provider import Provider

        providers = Database.get_default().get_providers(only_used=True)
        for provider in providers:
            accounts = Database.get_default().accounts_by_provider(provider.id)
            provider = Provider(*provider)
            _accounts = []
            for account in accounts:
                account = Account(*account)
                if account.otp:
                    _accounts.append(account)
            self._accounts_per_provider.append((provider, _accounts))
        self.props.empty = len(self._accounts_per_provider) == 0
