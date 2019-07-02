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
from gi.repository import Gtk, GObject, GLib
from .edit import EditAccountWindow


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_row.ui')
class AccountRow(Gtk.ListBoxRow):
    """
        AccountRow Widget.

        It's a subclass of Gtk.ListBoxRow
        Added as a child to a AccountsList

        @signals: None
        @properties: account
    """
    __gtype_name__ = 'AccountRow'

    __gsignals__ = {
        'pin-copied': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,)
        ),
        'account-updated': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,)
        ),
    }

    account_name_label: Gtk.Label = Gtk.Template.Child()
    pin_label: Gtk.Label = Gtk.Template.Child()

    more_actions_btn: Gtk.Button = Gtk.Template.Child()
    delete_btn: Gtk.Button = Gtk.Template.Child()
    copy_btn_stack: Gtk.Stack = Gtk.Template.Child()

    _timeout_id: int = 0

    def __init__(self, account):
        """
        :param account: Account
        """
        super(AccountRow, self).__init__()
        self.init_template('AccountRow')
        self._account = account

        self._account.connect("otp_updated", self._on_pin_updated)
        self.__init_widgets()

    @property
    def account(self):
        """
            The Account model assigned to this AccountRow

            :return: Account Object
        """
        return self._account

    def __init_widgets(self):
        # Set up account name text label
        self.account_name_label.set_text(self.account.username)
        self.account_name_label.set_tooltip_text(self.account.username)

        # Set up account pin text label
        pin = self.account.otp.pin
        if pin:
            self.pin_label.set_text(pin)
        else:
            self.pin_label.set_text("??????")
            self.pin_label.set_tooltip_text(_("Couldn't generate the secret code"))

    @Gtk.Template.Callback('copy_btn_clicked')
    def _on_copy(self, *__):
        """
            Copy button clicked signal handler.
            Copies the OTP pin to the clipboard
        """
        self.copy_btn_stack.set_visible_child_name("ok_image")
        self._account.copy_pin()
        self.emit("pin-copied", _("The PIN of {} was copied to the clipboard").format(self.account.username))

        def btn_clicked_timeout_callback(*_):
            self.copy_btn_stack.set_visible_child_name("copy_image")
            if self._timeout_id > 0:
                GLib.Source.remove(self._timeout_id)
                self._timeout_id = 0

        self._timeout_id = GLib.timeout_add_seconds(2,
                                                    btn_clicked_timeout_callback,
                                                    None)

    @Gtk.Template.Callback('edit_btn_clicked')
    def _on_edit(self, *_):
        """
            Edit Button clicked signal handler.
            Opens a new Window to edit the current account.
        """
        from Authenticator.widgets import Window
        main_window = Window.get_default()
        edit_window = EditAccountWindow(self._account)
        edit_window.set_transient_for(main_window)
        edit_window.set_size_request(*main_window.get_size())
        edit_window.resize(*main_window.get_size())
        edit_window.connect("updated", self._on_update)
        edit_window.show_all()
        edit_window.present()

    def _on_update(self, __, account_name: str, provider):
        """
            On account update signal handler.
            Updates the account name and provider

            :param account_name: the new account's name
            :type account_name: str

            :param provider: the new account's provider
            :type provider: str
        """
        self.account_name_label.set_text(account_name)
        self.account.update(account_name, provider)
        self.emit("account-updated", _("The account was updated successfully"))

    def _on_pin_updated(self, _, pin: str):
        """
            Updates the pin label each time a new OTP is generated.
            otp_updated signal handler.

            :param pin: the new OTP
            :type pin: str
        """
        if pin:
            self.pin_label.set_text(pin)
