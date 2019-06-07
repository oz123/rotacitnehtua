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
from gi.repository import Gio, Gtk, GObject, Handy
from Authenticator.models import Settings, Keyring

__all__ = ['SettingsWindow']


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/settings.ui')
class SettingsWindow(Handy.PreferencesWindow):
    __gtype_name__ = 'SettingsWindow'

    dark_theme_switch: Gtk.Switch = Gtk.Template.Child()
    night_light_switch: Gtk.Switch = Gtk.Template.Child()

    lock_row: Handy.ExpanderRow = Gtk.Template.Child()

    lock_timeout_row: Handy.ActionRow = Gtk.Template.Child()
    lock_timeout_spinbtn: Gtk.SpinButton = Gtk.Template.Child()

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.init_template('SettingsWindow')

        self.__init_widgets()
        self.__bind_signals()

    def __init_widgets(self):

        self._password_widget = PasswordWidget()
        self._password_widget.parent = self
        self.lock_row.add(self._password_widget)

    def _on_lock_row_expanded(self, *_):
        keyring = Keyring.get_default()
        if keyring.has_password():
            keyring.set_password_state(self.lock_row.props.expanded)
            self.lock_row_toggle_btn.props.active = False

    def __on_lock_switch_toggled(self, toggle_btn: Gtk.ToggleButton, *_):
        toggled = toggle_btn.props.active
        expansion_enabled = self.lock_row.props.enable_expansion
        if not Keyring.get_default().has_password() and not toggled and expansion_enabled:
            self.lock_row.props.enable_expansion = False

    def __bind_signals(self):
        settings = Settings.get_default()
        self.dark_theme_switch.set_active(settings.dark_theme and not settings.night_light)

        self.night_light_switch.set_active(settings.night_light)
        settings.bind("night-light", self.night_light_switch,
                      "active", Gio.SettingsBindFlags.DEFAULT)

        keyring = Keyring.get_default()
        # Hackish solution to get the expander from HdyExpanderRow
        self.lock_row.props.enable_expansion = keyring.has_password()
        self.lock_row_toggle_btn = self.lock_row.get_children()[0].get_children()[3]

        self.lock_row.props.enable_expansion = Keyring.get_default().is_password_enabled()
        self.lock_row.connect("notify::enable-expansion", self.__on_enable_password)
        self.lock_row_toggle_btn.connect("notify::active", self.__on_lock_switch_toggled)
        self.lock_row.connect("notify::expanded", self._on_lock_row_expanded)

        keyring.bind_property("can-be-locked", self.lock_timeout_row, "sensitive",
                              GObject.BindingFlags.DEFAULT | GObject.BindingFlags.SYNC_CREATE)
        self.lock_timeout_spinbtn.props.value = settings.auto_lock_timeout
        settings.bind("auto-lock-timeout", self.lock_timeout_spinbtn, "value",
                      Gio.SettingsBindFlags.DEFAULT)

        self._password_widget.connect("password-updated", self.__on_password_updated)
        self._password_widget.connect("password-deleted", self.__on_password_deleted)

        def on_night_light_switch(switch: Gtk.Switch, _):
            # Set the application to use Light theme
            if switch.get_active() and self.dark_theme_switch.get_active():

                self.dark_theme_switch.set_active(False)

        self.night_light_switch.connect("notify::active", on_night_light_switch)

        def on_dark_theme_switch(switch: Gtk.Switch, _):
            # Set the application to use Light theme

            if settings.night_light and switch.get_active():
                switch.set_state(False)
            elif not settings.night_light:
                settings.dark_theme = switch.get_active()

        self.dark_theme_switch.connect("notify::active", on_dark_theme_switch)

    def __on_enable_password(self, *_):
        keyring = Keyring.get_default()
        keyring.set_password_state(self.lock_row.props.enable_expansion)
        if not keyring.has_password():
            self._password_widget.set_current_password_visibility(False)
        else:
            self._password_widget.set_current_password_visibility(True)

    def __on_password_updated(self, *_):
        self.lock_row_toggle_btn.props.active = False

    def __on_password_deleted(self, *__):
        # self.notification.send(_("The authentication password was deleted."))
        self.lock_row.set_enable_expansion(False)
        self.lock_row_toggle_btn.props.active = False


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/password_widget.ui')
class PasswordWidget(Gtk.Box):
    __gtype_name__ = 'PasswordWidget'
    __gsignals__ = {
        'password-updated': (
            GObject.SignalFlags.RUN_LAST,
            None,
            ()
        ),
        'password-deleted': (
            GObject.SignalFlags.RUN_LAST,
            None,
            ()
        ),
    }

    delete_password_btn: Gtk.Button = Gtk.Template.Child()
    change_password_btn: Gtk.Button = Gtk.Template.Child()

    password_entry: Gtk.Entry = Gtk.Template.Child()
    confirm_password_entry: Gtk.Entry = Gtk.Template.Child()
    current_password_entry: Gtk.Entry = Gtk.Template.Child()

    current_password_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self):
        super(PasswordWidget, self).__init__()
        self.parent = None
        self.init_template('PasswordWidget')

    def reset_widgets(self):
        """Reset widgets state."""
        self.password_entry.set_text("")
        self.confirm_password_entry.set_text("")
        self.current_password_entry.set_text("")

        self.password_entry.get_style_context().remove_class("error")
        self.confirm_password_entry.get_style_context().remove_class("error")
        self.current_password_entry.get_style_context().remove_class("error")
        self.change_password_btn.set_sensitive(False)

    def set_current_password_visibility(self, visibilty: bool):
        if not visibilty:
            self.current_password_box.hide()
            self.delete_password_btn.hide()
            self.change_password_btn.set_label(_("Save Password"))
        else:
            self.current_password_box.show()
            self.delete_password_btn.show()
            self.change_password_btn.set_label(_("Change Password"))

    @Gtk.Template.Callback('password_entry_changed')
    def __validate_password(self, *_):
        keyring = Keyring.get_default()
        password = self.password_entry.get_text()
        repeat_password = self.confirm_password_entry.get_text()
        if not password:
            self.password_entry.get_style_context().add_class("error")
            valid_password = False
        else:
            self.password_entry.get_style_context().remove_class("error")
            valid_password = True

        if not repeat_password or password != repeat_password:
            self.confirm_password_entry.get_style_context().add_class("error")
            valid_repeat_password = False
        else:
            self.confirm_password_entry.get_style_context().remove_class("error")
            valid_repeat_password = True
        to_validate = [valid_password, valid_repeat_password]

        if keyring.has_password():
            old_password = self.current_password_entry.get_text()
            if old_password != keyring.get_password():
                self.current_password_entry.get_style_context().add_class("error")
                valid_old_password = False
            else:
                self.current_password_entry.get_style_context().remove_class("error")
                valid_old_password = True
            to_validate.append(valid_old_password)

        self.change_password_btn.set_sensitive(all(to_validate))

    @Gtk.Template.Callback('update_password_clicked')
    def __save_password(self, *__):
        if self.change_password_btn.get_sensitive():
            keyring = Keyring.get_default()
            password = self.password_entry.get_text()
            keyring.set_password(password)
            self.reset_widgets()
            self.set_current_password_visibility(True)
            self.emit("password-updated")

    @Gtk.Template.Callback('reset_password_clicked')
    def __reset_password(self, *args):
        dialog = Gtk.MessageDialog(buttons=Gtk.ButtonsType.YES_NO)
        dialog.props.message_type = Gtk.MessageType.QUESTION
        dialog.props.text = _("Do you want to remove the authentication password?")
        dialog.props.secondary_text = _("Authentication password enforces the privacy of your accounts.")

        dialog.set_transient_for(self.parent)

        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            Keyring.get_default().remove_password()
            self.reset_widgets()
            self.set_current_password_visibility(False)
            self.emit("password-deleted")
        dialog.destroy()
