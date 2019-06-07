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

from gi.repository import Gtk, GObject, GLib
from gettext import gettext as _


class Notification(Gtk.Revealer):

    show_close_btn = GObject.Property(type=bool, default=False)
    show_action_btn = GObject.Property(type=bool, default=False)

    timeout = GObject.Property(type=int, default=5)
    action_callback = None

    _action_signal = None
    _source = 0

    def __init__(self):
        Gtk.Revealer.__init__(self)
        self._message = ""
        self._build_widget()
        self._bind_signals()

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, new_message):
        self._message = new_message
        self._notification_lbl.set_text(new_message)

    def send(self, message, **kwargs):
        self.message = message

        self._action_btn.set_label(kwargs.get("action_label", _("Undo")))

        self.props.show_action_btn = kwargs.get("show_action_btn", False)
        self.props.show_close_btn = kwargs.get("show_close_btn", False)
        self.props.timeout = kwargs.get("timeout", self.props.timeout)
        self.action_callback = kwargs.get("action_callback")

        self.set_reveal_child(True)
        self._source_id = GLib.timeout_add_seconds(self.timeout,
                                                   self._delete_notification, None)

    def _build_widget(self):
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.set_transition_duration(400)
        self.set_reveal_child(False)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.CENTER)

        frame = Gtk.Frame()
        frame.get_style_context().add_class("app-notification")
        notification_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self._close_btn = Gtk.Button()
        self._close_btn.connect("clicked", self._delete_notification)
        close_img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        self._close_btn.get_style_context().add_class("flat")
        self._close_btn.set_tooltip_text(_("Close the notification"))
        self._close_btn.props.image = close_img
        self._close_btn.props_always_show_image = True

        self._action_btn = Gtk.Button()
        self._action_btn.set_label(_("Undo"))
        self._action_btn.connect("clicked", self._on_action_btn_clicked)

        self._notification_lbl = Gtk.Label()
        self._notification_lbl.set_text(self.message)

        notification_container.pack_start(self._notification_lbl, False, False, 6)
        notification_container.pack_end(self._close_btn, False, False, 6)
        notification_container.pack_end(self._action_btn, False, False, 6)

        frame.add(notification_container)
        self.add(frame)

    def _delete_notification(self, *args):
        self.set_reveal_child(False)
        self.message = ""
        if self._source_id > 0:
            GLib.Source.remove(self._source_id)

    def _on_action_btn_clicked(self, *args):
        if self.action_callback:
            self.action_callback()
        self._delete_notification()

    def _bind_signals(self):
        self._close_btn.bind_property("visible", self, "show-close-btn", GObject.BindingFlags.BIDIRECTIONAL)
        self._action_btn.bind_property("visible", self, "show-action-btn", GObject.BindingFlags.BIDIRECTIONAL)
