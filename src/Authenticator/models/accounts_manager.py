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
from typing import Iterable

from .account import Account
from .database import Database
from .provider import Provider


class AccountsManager(GObject.GObject):
    __gsignals__ = {
        'counter_updated': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (int,)
        ),
    }

    instance: 'AccountsManager' = None
    empty: GObject.Property = GObject.Property(type=bool, default=False)

    # A list that contains a tuple (provider, accounts)
    __accounts = []

    def __init__(self):
        GObject.GObject.__init__(self)
        self._accounts_per_provider = []
        self._alive = True
        self.__fill_accounts()
        self._timeout_id = 0
        self.counter_max = 30
        self.counter = self.counter_max
        self._start_progress_countdown()

    @staticmethod
    def get_default() -> 'AccountsManager':
        if AccountsManager.instance is None:
            AccountsManager.instance = AccountsManager()
        return AccountsManager.instance

    def add(self, provider: 'Provider', account: 'Account'):
        added = False
        for _provider, accounts in self._accounts_per_provider:
            if provider == _provider:
                accounts.append(account)
                added = True
                break
        if not added:
            self._accounts_per_provider.append((provider, [account]))
        self.props.empty = False
        if self._timeout_id == 0:
            self._start_progress_countdown()

    def delete(self, account: 'Account'):
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
        if self.props.empty:
            self._stop_progress_countdown()

    def search(self, terms: Iterable[str]):
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

    def kill(self):
        self._alive = False
        self._stop_progress_countdown()

    def update_childes(self, signal: str):
        for _, accounts in self._accounts_per_provider:
            for account in accounts:
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

    def _start_progress_countdown(self):
        self._stop_progress_countdown()
        self._timeout_id = GLib.timeout_add_seconds(1, self.__update_counter,
                                                    None)

    def _stop_progress_countdown(self):
        if self._timeout_id > 0:
            GLib.Source.remove(self._timeout_id)
            self._timeout_id = 0
        self.counter = self.counter_max
