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
from gi.repository import Gdk, Gtk, GObject, Gio, Handy

from .list import AccountsWidget
from Authenticator.widgets.notification import Notification
from Authenticator.widgets.provider_image import ProviderImage, ProviderImageState
from Authenticator.models import AccountsManager, Account, OTP, Provider, QRReader, GNOMEScreenshot


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_add.ui')
class AddAccountWindow(Gtk.Window):
    """Add Account Window."""
    __gtype_name__ = "AddAccountWindow"
    # Widgets
    add_btn: Gtk.Button = Gtk.Template.Child()
    scan_btn: Gtk.Button = Gtk.Template.Child()
    back_btn: Gtk.Button = Gtk.Template.Child()

    column: Handy.Column = Gtk.Template.Child()

    def __init__(self):
        super(AddAccountWindow, self).__init__()
        self.init_template('AddAccountWindow')
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        self.__init_widgets()

    def __init_widgets(self):
        """Create the Add Account widgets."""
        self.account_config = AccountConfig()
        self.account_config.connect("changed", self._on_account_config_changed)

        self.scan_btn.connect("clicked", self.account_config.scan_qr)
        self.back_btn.connect("clicked", lambda *_: self.destroy())
        self.column.add(self.account_config)

    def _on_account_config_changed(self, _, state: bool):
        """Set the sensitivity of the AddButton depends on the AccountConfig."""
        self.add_btn.set_sensitive(state)

    @Gtk.Template.Callback('add_btn_clicked')
    def _on_add(self, *_):
        account_obj = self.account_config.account
        # Create a new account
        account = Account.create(account_obj["username"],
                                 account_obj["token"],
                                 account_obj["provider"].provider_id)
        # Add it to the AccountsManager
        AccountsManager.get_default().add(account_obj["provider"], account)
        AccountsWidget.get_default().append(account)
        self.destroy()


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_config.ui')
class AccountConfig(Gtk.Overlay):
    __gtype_name__ = 'AccountConfig'
    # Signals
    __gsignals__ = {
        'changed': (
            GObject.SignalFlags.RUN_LAST,
            None, (bool,)
        ),
    }
    # Properties
    is_edit = GObject.Property(type=bool, default=False)
    # Widgets
    main_container: Gtk.Box = Gtk.Template.Child()

    proivder_image: ProviderImage

    provider_combobox = Gtk.Template.Child()
    providers_store = Gtk.Template.Child()
    provider_entry: Gtk.Entry = Gtk.Template.Child()

    account_name_entry: Gtk.Entry = Gtk.Template.Child()
    provider_website_entry: Gtk.Entry = Gtk.Template.Child()
    token_entry: Gtk.Entry = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super(AccountConfig, self).__init__()
        self.init_template('AccountConfig')

        self.props.is_edit = kwargs.get("edit", False)
        self._account = kwargs.get("account", None)
        self._notification = Notification()
        self.__init_widgets()

    @property
    def account(self):
        """
            Return an instance of Account for the new account.
        """
        provider_name = self.provider_entry.get_text()
        provider = Provider.get_by_name(provider_name)

        # Create a new provider if we don't find one
        if not provider:
            provider_image = self.provider_image.image
            provider_website = self.provider_website_entry.get_text()
            provider = Provider.create(provider_name, provider_website, None,
                                       provider_image)
        # Update the provider image if it changed
        elif provider and self.provider_image.image != provider.image:
            provider.update(image=self.provider_image.image)

        account = {
            "username": self.account_name_entry.get_text(),
            "provider": provider
        }
        if not self.props.is_edit:
            # remove spaces
            token = self.token_entry.get_text()
            account["token"] = "".join(token.split())
        return account

    def __init_widgets(self):
        self.add_overlay(self._notification)
        if self._account is not None:
            self.provider_image = ProviderImage(self._account.provider,
                                                96)
            self.token_entry.props.secondary_icon_activatable = self._account.provider.doc_url is not None
        else:
            self.token_entry.props.secondary_icon_activatable = False
            self.provider_image = ProviderImage(None, 96)

        self.main_container.pack_start(self.provider_image, False, False, 0)
        self.main_container.reorder_child(self.provider_image, 0)
        self.provider_image.set_halign(Gtk.Align.CENTER)

        # Set up auto completion
        if self._account and self._account.provider:
            self.provider_entry.set_text(self._account.provider.name)

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
        provider = Provider.get_by_name(provider_name)
        if provider and provider.doc_url:
            Gio.app_info_launch_default_for_uri(provider.doc_url)
        else:
            self.token_entry.props.secondary_icon_activatable = False

    @Gtk.Template.Callback('provider_changed')
    def _on_provider_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            provider_id = model[tree_iter][0]
            provider = Provider.get_by_id(provider_id)
        else:
            provider_name = self.provider_entry.get_text()
            provider = Provider.get_by_name(provider_name)
        # if we find a provider already saved on the database
        if provider:
            self.token_entry.props.secondary_icon_activatable = provider.doc_url is not None
            self.provider_image.emit("provider-changed", provider)
            self.provider_website_entry.hide()
            self.provider_website_entry.set_no_show_all(True)
        else:
            self.provider_website_entry.show()
            self.provider_website_entry.set_no_show_all(False)
            self.provider_image.set_state(ProviderImageState.NOT_FOUND)

    def _fill_data(self):
        providers = Provider.all()
        for provider in providers:
            self.providers_store.append([provider.provider_id, provider.name])

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

    @Gtk.Template.Callback('on_provider_website_changed')
    def on_provider_website_changed(self, entry, event):
        '''Update the website favicon once the URL is updated'''
        if entry.get_visible():
            website = entry.get_text().strip()
            self.provider_image.fetch_favicon_from_url(website)

    def scan_qr(self, *args):
        '''Scans a QRCode and fills the entries with the correct data.'''
        try:
            filename = GNOMEScreenshot.area()
            assert filename
            account = QRReader.from_file(filename)
            assert account is dict
            self.token_entry.set_text(account.get('token',
                                                  self.token_entry.get_text()))
            self.provider_entry.set_text(account.get('provider',
                                                     self.provider_entry.get_text()))
            self.account_name_entry.set_text(account.get('username',
                                                         self.account_name_entry.get_text()))
        except AssertionError:
            self._notification.send(_("Invalid QR code"),
                                    timeout=3)
