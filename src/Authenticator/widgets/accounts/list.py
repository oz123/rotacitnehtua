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
from gettext import gettext as _
from gi.repository import Gtk, GObject

from Authenticator.widgets.provider_image import ProviderImage
from .row import AccountRow
from Authenticator.models import Account, AccountsManager, Provider


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/accounts_widget.ui')
class AccountsWidget(Gtk.Box):
    __gtype_name__ = 'AccountsWidget'

    __gsignals__ = {
        'account-removed': (GObject.SignalFlags.RUN_LAST, None, ()),
        'account-added': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    instance: 'AccountsWidget' = None

    accounts_container = Gtk.Template.Child()
    otp_progress_bar = Gtk.Template.Child()

    def __init__(self):
        super(AccountsWidget, self).__init__()
        self.init_template('AccountsWidget')

        self._providers = []
        self._to_delete = []
        self.__init_widgets()

    def __init_widgets(self):
        accounts_manager = AccountsManager.get_default()
        accounts_manager.connect("counter_updated",
                                 self._on_counter_updated)
        # Add different accounts to the main view
        for provider, accounts in accounts_manager.accounts_per_provider:
            for account in accounts:
                self.append(account)

    def __add_provider(self, provider):
        accounts_list = self._get_by_provider(provider)["accounts_list"]
        if not accounts_list:
            accounts_list = AccountsList()
            accounts_list.connect("account-deleted", self._on_account_deleted)
            self._providers.append({"provider": provider,
                                    "accounts_list": accounts_list})
            provider_widget = ProviderWidget(accounts_list, provider)
            self.accounts_container.pack_start(provider_widget, False, False, 0)
        return accounts_list

    def _get_by_provider(self, provider):
        for provider_info in self._providers:
            if provider.provider_id == provider_info['provider'].provider_id:
                return provider_info
        return {
            'provider': None,
            'accounts_list': None
        }

    @staticmethod
    def get_default() -> 'AccountsWidget':
        """Return the default instance of AccountsWidget."""
        if AccountsWidget.instance is None:
            AccountsWidget.instance = AccountsWidget()
        return AccountsWidget.instance

    def append(self, account):
        accounts_list = self.__add_provider(account.provider)
        accounts_list.add_row(account)

        self._reorder()
        self.emit("account-added")

    @property
    def accounts_lists(self):
        return [provider['accounts_list'] for provider in self._providers]

    def update_provider_image(self, provider):
        for child in self.accounts_container.get_children():
            if child.provider.provider_id == provider.provider_id:
                child.provider_image.set_image(provider.image)
                break

    def update_provider(self, account, new_provider):
        current_account_list = None
        account_row = None
        for account_list in self.accounts_lists:
            for account_row in account_list:
                if account_row.account == account:
                    current_account_list = account_list
                    break

            if current_account_list:
                break
        if account_row:
            current_account_list.remove(account_row)
            account_row.account.provider = new_provider
            self.append(account_row.account)
        self._on_account_deleted(current_account_list, None)
        self._reorder()
        self._clean_unneeded_providers_widgets()

    def _on_account_deleted(self, accounts_list, account=None):
        if account:
            AccountsManager.get_default().delete(account)
        if len(accounts_list.get_children()) == 0:
            self._to_delete.append(accounts_list)
        self._reorder()
        self._clean_unneeded_providers_widgets()
        self.emit("account-removed")

    def _clean_unneeded_providers_widgets(self):
        for accounts_list in self._to_delete:
            provider_widget = accounts_list.get_parent()
            self.accounts_container.remove(provider_widget)
            self._providers.remove(self._get_by_provider(provider_widget.provider))
        self._to_delete = []

    def _reorder(self):
        """
            Re-order the ProviderWidget on AccountsWidget.
        """
        childs = self.accounts_container.get_children()
        ordered_childs = sorted(
            childs, key=lambda children: children.provider.name.lower())
        for i in range(len(ordered_childs)):
            self.accounts_container.reorder_child(ordered_childs[i], i)
        self.show_all()

    def _on_counter_updated(self, accounts_manager, counter):
        counter_fraction = counter / accounts_manager.counter_max
        self.otp_progress_bar.set_fraction(counter_fraction)
        self.otp_progress_bar.set_tooltip_text(
            _("The One-Time Passwords expire in {} seconds").format(counter))


class ProviderWidget(Gtk.Box):

    def __init__(self, accounts_list: Gtk.ListBox, provider: Provider):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class("provider-widget")
        self.provider = provider
        self.accounts_list = accounts_list
        self._build_widgets()

    def _build_widgets(self):
        self.set_valign(Gtk.Align.START)

        provider_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        provider_lbl = Gtk.Label()
        provider_lbl.set_text(self.provider.name)
        provider_lbl.set_halign(Gtk.Align.START)
        provider_lbl.get_style_context().add_class("provider-name")

        self.provider_image = ProviderImage(self.provider, 48)

        provider_container.pack_start(self.provider_image, False, False, 6)
        provider_container.pack_start(provider_lbl, False, False, 6)

        self.pack_start(provider_container, False, False, 6)
        self.pack_start(self.accounts_list, False, False, 6)


class AccountsList(Gtk.ListBox):
    """Accounts List."""

    __gsignals__ = {
        'account-deleted': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (Account, )
        ),
        'account-added': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (Account, )
        )
    }

    def __init__(self):
        Gtk.ListBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.get_style_context().add_class("accounts-list")
        self.get_style_context().add_class("frame")
        self.set_header_func(self._update_header_func)

    def add_row(self, account: Account):
        row = AccountRow(account)
        row.delete_btn.connect("clicked", self.__on_delete_child, row)
        self.add(row)
        self.emit("account-added", account)

    def __on_delete_child(self, _, account_row):
        self.remove(account_row)
        account = account_row.account
        account.remove()
        self.emit("account-deleted", account)

    def _update_header_func(self, row, row_before):
        def on_realize_sep(separator):
            separator.set_size_request(row_before.get_allocated_width(), -1)

        if row_before:
            separator = Gtk.Separator()
            separator.connect("realize", on_realize_sep)
            row.set_header(separator)
            separator.show()
