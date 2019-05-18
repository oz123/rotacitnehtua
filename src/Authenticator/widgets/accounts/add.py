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
import asyncio
from gettext import gettext as _
from gi.repository import Gtk, GObject, GLib, Gio

from Authenticator.widgets.notification import Notification
from Authenticator.widgets.provider_image import ProviderImage
from Authenticator.models import OTP, ProviderManager, FaviconManager


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_add.ui')
class AddAccountWindow(Gtk.Window):
    """Add Account Window."""

    __gtype_name__ = "AddAccountWindow"

    add_btn = Gtk.Template.Child()
    overlay = Gtk.Template.Child()

    def __init__(self):
        super(AddAccountWindow, self).__init__()
        self.init_template('AddAccountWindow')
        self.__init_widgets()

    def __init_widgets(self):
        """Create the Add Account widgets."""
        self.notification = Notification()
        self.overlay.add_overlay(self.notification)

        self.account_config = AccountConfig()
        self.account_config.connect("changed", self._on_account_config_changed)

        self.overlay.add(self.account_config)

    @Gtk.Template.Callback('scan_btn_clicked')
    def _on_scan(self, *__):
        """
            QR Scan button clicked signal handler.
        """
        if self.account_config and not self.account_config.scan_qr():
            self.notification.send(_("Invalid QR code"),
                                   timeout=3)

    def _on_account_config_changed(self, _, state):
        """Set the sensitivity of the AddButton depends on the AccountConfig."""
        self.add_btn.set_sensitive(state)

    @Gtk.Template.Callback('close_btn_clicked')
    def _on_quit(self, *_):
        self.destroy()

    @Gtk.Template.Callback('add_btn_clicked')
    def _on_add(self, *_):
        from .list import AccountsWidget
        from ...models import AccountsManager, Account
        account_obj = self.account_config.account
        # Create a new account
        account = Account.create(account_obj["username"],
                                 account_obj["provider"],
                                 account_obj["token"],
                                 account_obj["image_path"])
        # Add it to the AccountsManager
        AccountsManager.get_default().add(account)
        AccountsWidget.get_default().append(account)
        self._on_quit()

@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_config.ui')
class AccountConfig(Gtk.Box, GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
    }

    __gtype_name__ = 'AccountConfig'
    is_edit = GObject.Property(type=bool, default=False)

    main_box = Gtk.Template.Child()
    proivder_image = None

    account_name_entry = Gtk.Template.Child()
    token_entry = Gtk.Template.Child()
    provider_combobox = Gtk.Template.Child()
    provider_entry = Gtk.Template.Child()
    providers_store = Gtk.Template.Child()

    provider_completion = Gtk.Template.Child()
    notification = Gtk.Template.Child()
    notification_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super(AccountConfig, self).__init__()
        self.init_template('AccountConfig')
        GObject.GObject.__init__(self)

        self.props.is_edit = kwargs.get("edit", False)
        self._account = kwargs.get("account", None)

        self.__init_widgets()

    @property
    def account(self):
        """
            Return an instance of Account for the new account.
        """
        account = {
            "username": self.account_name_entry.get_text(),
            "provider": self.provider_entry.get_text(),
            "image_path": self.provider_image.get_path()
        }

        if not self.props.is_edit:
            # remove spaces
            token = self.token_entry.get_text()
            account["token"] = "".join(token.split())
        return account

    def __init_widgets(self):

        self.provider_image = ProviderImage(self._account.provider, self._account.image_path,
                                             96, True)
        self.main_box.pack_start(self.provider_image, False, False, 0)
        self.main_box.reorder_child(self.provider_image, 0)
        self.provider_image.set_halign(Gtk.Align.CENTER)

        # Set up auto completion
        if self._account and self._account.provider:
            self.provider_entry.set_text(self._account.provider)

        if self._account and self._account.username:
            self.account_name_entry.set_text(self._account.username)

        if self.props.is_edit:
            self.token_entry.hide()
            self.token_entry.set_no_show_all(True)
        else:
            self.token_entry.connect("icon-press", self.__on_open_doc_url)

        self._fill_data()

    def __on_open_doc_url(self, *args):
        provider_name = self.provider_entry.get_text()
        provider = ProviderManager.get_default().get_by_name(provider_name)
        if provider and provider.doc:
            Gio.app_info_launch_default_for_uri(provider.doc)

    @Gtk.Template.Callback('provider_changed')
    def _on_provider_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            provider_name = model[tree_iter][0]
        else:
            entry = combo.get_child()
            provider_name = entry.get_text()

        provider = ProviderManager.get_default().get_by_name(provider_name)
        self.token_entry.props.secondary_icon_activatable = provider is not None
        self._validate()
        self.provider_image.set_property('provider', provider_name)

    def _fill_data(self):
        providers = ProviderManager.get_default().providers
        for provider in providers:
            self.providers_store.append([provider.name])

    @Gtk.Template.Callback('account_edited')
    def _validate(self, *_):
        """Validate the username and the token."""
        provider = self.provider_entry.get_text()
        username = self.account_name_entry.get_text()
        token = "".join(self.token_entry.get_text().split())

        if not username:
            self.account_name_entry.get_style_context().add_class("error")
            valid_name = False
        else:
            self.account_name_entry.get_style_context().remove_class("error")
            valid_name = True

        if not provider:
            self.provider_combobox.get_style_context().add_class("error")
            valid_provider = False
        else:
            self.provider_combobox.get_style_context().remove_class("error")
            valid_provider = True

        if (not token or not OTP.is_valid(token)) and not self.props.is_edit:
            self.token_entry.get_style_context().add_class("error")
            valid_token = False
        else:
            self.token_entry.get_style_context().remove_class("error")
            valid_token = True
        self.emit("changed", all([valid_name, valid_provider, valid_token]))

    def scan_qr(self):
        """
            Scans a QRCode and fills the entries with the correct data.
        """
        from ...models import QRReader, GNOMEScreenshot
        filename = GNOMEScreenshot.area()
        if filename:
            qr_reader = QRReader(filename)
            secret = qr_reader.read()
            if qr_reader.is_valid():
                self.token_entry.set_text(secret)
                if qr_reader.provider is not None:
                    self.provider_entry.set_text(qr_reader.provider)
                if qr_reader.username is not None:
                    self.account_name_entry.set_text(qr_reader.username)
            return qr_reader.is_valid()
