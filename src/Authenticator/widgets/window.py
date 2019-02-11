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
require_version('Gd', '1.0')
require_version("Gtk", "3.0")
from gi.repository import Gd, Gtk, GObject, Gio, GLib
from ..models import Logger, Settings, Database, AccountsManager
from .headerbar import HeaderBar, HeaderBarState
from .accounts import AccountsWidget, AddAccountWindow
from .search_bar import SearchBar
from . import LoginWidget

class WindowState:
    NORMAL = 0
    LOCKED = 1
    EMPTY  = 2


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/window.ui')
class Window(Gtk.ApplicationWindow, GObject.GObject):
    """Main Window object."""
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'locked': (GObject.SignalFlags.RUN_LAST, None, ()),
        'unlocked': (GObject.SignalFlags.RUN_LAST, None, ())
    }

    __gtype_name__ = 'Window'

    # Default Window instance
    instance = None

    is_empty = GObject.Property(type=bool, default=False)
    state = GObject.Property(type=int, default=0)

    headerbar = Gtk.Template.Child()

    add_btn = Gtk.Template.Child()
    search_btn = Gtk.Template.Child()

    main_stack = Gtk.Template.Child()

    search_bar = Gtk.Template.Child()

    notification = Gtk.Template.Child()
    notification_label = Gtk.Template.Child()

    accounts_viewport = Gtk.Template.Child()

    def __init__(self):
        super(Window, self).__init__()
        self.init_template('Window')

        self.connect("locked", self.__on_locked)
        self.connect("unlocked", self.__on_unlocked)

        self.key_press_signal = None
        self.restore_state()
        # Start the Account Manager
        AccountsManager.get_default()

        self.__init_widgets()

    @staticmethod
    def get_default():
        """Return the default instance of Window."""
        if Window.instance is None:
            Window.instance = Window()
        return Window.instance

    def close(self):
        self.save_state()
        AccountsManager.get_default().kill()
        self.destroy()

    def add_account(self, *_):
        if not self.get_application().is_locked:
            add_window = AddAccountWindow()
            add_window.set_transient_for(self)
            add_window.show_all()
            add_window.present()

    def update_view(self, *_):
        count = Database.get_default().count
        self.set_property("is-empty", count == 0)
        if not self.is_empty:
            self.main_stack.set_visible_child_name("normal_state")
            child_name = "normal_state"
            self.props.state = WindowState.NORMAL
        else:
            self.main_stack.set_visible_child_name("empty_state")
            child_name = "empty_state"
            self.props.state = WindowState.EMPTY

    def toggle_search(self, *_):
        """
            Switch the state of the search mode

            Switches the state of the search mode if:
                - The application is not locked
                - There are at least one account in the database
            return: None
        """
        if not (self.get_application().is_locked or self.is_empty):
            toggled = not self.search_bar.get_property("search_mode_enabled")
            self.search_bar.set_property("search_mode_enabled", toggled)

    def save_state(self):
        """
            Save window position and maximized state.
        """
        settings = Settings.get_default()
        settings.window_position = self.get_position()
        settings.window_maximized = self.is_maximized()

    def restore_state(self):
        """
            Restore the window's state.
        """
        settings = Settings.get_default()
        # Restore the window position
        position_x, position_y = settings.window_position
        if position_x != 0 and position_y != 0:
            self.move(position_x, position_y)
            Logger.debug("[Window] Restore position x: {}, y: {}".format(position_x,
                                                                         position_y))
        else:
            # Fallback to the center
            self.set_position(Gtk.WindowPosition.CENTER)

        if settings.window_maximized:
            self.maximize()

    def __init_widgets(self):
        """Build main window widgets."""

        # Register Actions
        self.__add_action("add-account", self.add_account)
        self.__add_action("toggle-searchbar", self.toggle_search)

        # Set up accounts Widget
        accounts_widget = AccountsWidget.get_default()
        accounts_widget.connect("changed", self.update_view)
        self.accounts_viewport.add(accounts_widget)

        # Login Widget
        login_widget = LoginWidget.get_default()
        login_widget.login_btn.connect("clicked", self.__on_unlock)
        self.main_stack.add_named(login_widget, "login")

        self.update_view()

    def _on_account_delete(self, *_):
        self.update_view()

    def __on_delete_clicked(self, *__):
        self.notification_label.set_text(_("An account or more were removed."))
        self.notification.set_reveal_child(True)
        GLib.timeout_add_seconds(5,
                                lambda _: self.notification.set_reveal_child(False), None)


    def __on_locked(self, *_):
        if self.key_press_signal:
            self.disconnect(self.key_press_signal)
        self.props.state = WindowState.LOCKED
        self.main_stack.set_visible_child_name("login")

    def __on_unlocked(self, *_):
        self.update_view()

    def __on_unlock(self, *_):
        from ..models import Keyring
        login_widget = LoginWidget.get_default()
        typed_password = login_widget.password
        if typed_password == Keyring.get_password():
            self.get_application().set_property("is-locked", False)
            login_widget.set_has_error(False)
            login_widget.password = ""
            self.key_press_signal = self.connect("key-press-event", lambda x,
                                                y: self.search_bar.handle_event(y))
            self.update_view()
        else:
            login_widget.set_has_error(True)

    def __add_action(self, key, callback, prop_bind=None, bind_flag=GObject.BindingFlags.INVERT_BOOLEAN):
        action = Gio.SimpleAction.new(key, None)
        action.connect("activate", callback)
        if prop_bind:
            self.bind_property(prop_bind, action, "enabled", bind_flag)
        self.add_action(action)
