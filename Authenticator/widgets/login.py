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

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio



class LoginWidget(Gtk.Box):
    instance = None

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.login_btn = Gtk.Button()
        self._password_entry = Gtk.Entry()

        self._build_widgets()

    @staticmethod
    def get_default():
        if LoginWidget.instance is None:
            LoginWidget.instance = LoginWidget()
        return LoginWidget.instance

    def _build_widgets(self):
        self.set_border_width(36)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.FILL)

        info_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_container.set_valign(Gtk.Align.START)

        gicon = Gio.ThemedIcon(name="dialog-password-symbolic")
        image = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.DIALOG)

        label = Gtk.Label()
        label.set_text(_("Authenticator is locked"))
        label.get_style_context().add_class("loginwidget-mainlabel")

        sub_label = Gtk.Label()
        sub_label.set_text(_("Enter password to unlock"))
        sub_label.get_style_context().add_class("loginwidget-sublabel")

        info_container.pack_start(image, False, False, 6)
        info_container.pack_start(label, False, False, 3)
        info_container.pack_start(sub_label, False, False, 3)

        password_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._password_entry.set_placeholder_text(_("Type your password here"))
        self._password_entry.set_visibility(False)
        self._password_entry.grab_focus_without_selecting()

        self.login_btn.set_label(_("Unlock"))

        password_container.pack_start(self._password_entry, False, False, 3)
        password_container.pack_start(self.login_btn, False, False, 3)
        password_container.set_valign(Gtk.Align.CENTER)

        self.pack_start(info_container, False, False, 3)
        self.pack_start(password_container, True, False, 3)

    def set_has_error(self, has_errors):
        if has_errors:
            self._password_entry.get_style_context().add_class("error")
        else:
            self._password_entry.get_style_context().remove_class("error")

    @property
    def password(self):
        return self._password_entry.get_text()

    @password.setter
    def password(self, new_password):
        self._password_entry.set_text(new_password)
