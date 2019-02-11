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

from gi.repository import Gio, GLib, Gtk, GObject
from .window import Window
from ..models import Settings, Keyring

class SettingsView:
    MAIN = 0
    PASSWORD = 1


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/settings.ui')
class SettingsWindow(Gtk.Window):

    __gtype_name__ = 'SettingsWindow'

    lock_switch = Gtk.Template.Child()
    dark_theme_switch = Gtk.Template.Child()

    headerbar = Gtk.Template.Child()

    headerbar_stack = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()

    save_btn = Gtk.Template.Child()

    password_entry = Gtk.Template.Child()
    repeat_password_entry = Gtk.Template.Child()

    notification = Gtk.Template.Child()
    notification_label = Gtk.Template.Child()

    view = GObject.Property(type=int)

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.init_template('SettingsWindow')

        self.connect("notify::view", self.__update_view)

        self.__init_widgets()

    def __init_widgets(self):
        settings = Settings.get_default()
        settings.bind("night-mode", self.dark_theme_switch, "state", Gio.SettingsBindFlags.DEFAULT)

        self.lock_switch.set_active(Keyring.get_default().has_password())

    @Gtk.Template.Callback('lock_switch_state_changed')
    def __on_app_set_password(self, __, state):
        if state and not Keyring.get_default().has_password():
            self.props.view = SettingsView.PASSWORD
        else:
            Keyring.get_default().clear_password()
            self.__send_notification(_("Authentication password was unset. Please restart the application"))

    @Gtk.Template.Callback('save_btn_clicked')
    def __save_password(self, *__):
        if self.save_btn.get_sensitive():
            password = self.password_entry.get_text()
            Keyring.set_password(password)
            self.props.view = SettingsView.MAIN
            self.__send_notification(_("Authentication password is now enabled. Please restart the application."))

    @Gtk.Template.Callback('back_btn_clicked')
    def __back_btn_clicked(self, *_):
        self.props.view = SettingsView.MAIN
        if not Keyring.get_default().has_password():
            self.lock_switch.set_active(False)

    @Gtk.Template.Callback('dark_theme_switch_state_changed')
    @staticmethod
    def __on_dark_theme_changed(_, state):
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  state)

    @Gtk.Template.Callback('password_entry_changed')
    def __validate_password(self, *_):
        password = self.password_entry.get_text()
        repeat_password = self.repeat_password_entry.get_text()
        if not password:
            self.password_entry.get_style_context().add_class("error")
            valid_password = False
        else:
            self.password_entry.get_style_context().remove_class("error")
            valid_password = True

        if not repeat_password or password != repeat_password:
            self.repeat_password_entry.get_style_context().add_class("error")
            valid_repeat_password = False
        else:
            self.repeat_password_entry.get_style_context().remove_class("error")
            valid_repeat_password = True

        to_validate = [valid_password, valid_repeat_password]

        self.save_btn.set_sensitive(all(to_validate))

    def __update_view(self, *_):
        if self.props.view == SettingsView.PASSWORD:
            self.main_stack.set_visible_child_name("password_view")
            self.headerbar_stack.set_visible_child_name("headerbar_password")
            self.headerbar.set_show_close_button(False)
            self.notification.set_reveal_child(False)
            self.notification_label.set_text("")
        else:
            self.main_stack.set_visible_child_name("settings_view")
            self.headerbar_stack.set_visible_child_name("headerbar_settings")
            self.headerbar.set_show_close_button(True)
            # Reset Password View
            # To avoid user saving a password he doesn't remember
            self.password_entry.set_text("")
            self.repeat_password_entry.set_text("")
            self.password_entry.get_style_context().remove_class("error")
            self.repeat_password_entry.get_style_context().remove_class("error")
            self.save_btn.set_sensitive(False)

    def __send_notification(self, message):
        self.notification_label.set_text(message)
        self.notification.set_reveal_child(True)

        GLib.timeout_add_seconds(5,
                                lambda _: self.notification.set_reveal_child(False), None)
