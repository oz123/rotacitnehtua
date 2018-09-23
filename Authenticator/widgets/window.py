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
from gi.repository import Gd, Gtk, GObject
from ..models import Logger, Settings, Database, AccountsManager
from .headerbar import HeaderBar, HeaderBarState
from .accounts import AccountsWidget, AccountsListState, AddAccountWindow, EmptyAccountsList
from .search_bar import SearchBar
from .actions_bar import ActionsBar
from . import LoginWidget


class Window(Gtk.ApplicationWindow, GObject.GObject):
    """Main Window object."""
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (bool,)),
        'locked': (GObject.SignalFlags.RUN_LAST, None, ()),
        'unlocked': (GObject.SignalFlags.RUN_LAST, None, ())
    }

    # Default Window instance
    instance = None

    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        self.set_icon_name("com.github.bilelmoussaoui.Authenticator")
        self.get_style_context().add_class("authenticator-window")
        self.resize(550, 600)
        self.connect("locked", self.__on_locked)
        self.connect("unlocked", self.__on_unlocked)
        self.key_press_signal = None
        self.restore_state()
        AccountsManager.get_default()
        self._build_widgets()
        self.show_all()

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

    def set_menu(self, gio_menu):
        """Set Headerbar popover menu."""
        HeaderBar.get_default().generate_popover_menu(gio_menu)

    def add_account(self, *_):
        add_window = AddAccountWindow()
        add_window.set_transient_for(self)
        add_window.show_all()
        add_window.present()

    def update_view(self, *_):
        header_bar = HeaderBar.get_default()
        count = Database.get_default().count
        if count != 0:
            child_name = "accounts-list"
            header_bar.set_state(HeaderBarState.NORMAL)
        else:
            header_bar.set_state(HeaderBarState.EMPTY)
            child_name = "empty-accounts-list"
        child = self.main_stack.get_child_by_name(child_name)
        child.show_all()
        self.main_stack.set_visible_child(child)

    @staticmethod
    def toggle_select(*_):
        """
            Toggle select mode
        """
        header_bar = HeaderBar.get_default()
        accounts_widget = AccountsWidget.get_default()
        if header_bar.state == HeaderBarState.NORMAL:
            header_bar.set_state(HeaderBarState.SELECT)
            accounts_widget.set_state(AccountsListState.SELECT)
        else:
            header_bar.set_state(HeaderBarState.NORMAL)
            accounts_widget.set_state(AccountsListState.NORMAL)

    def save_state(self):
        """Save window position & size."""
        settings = Settings.get_default()
        settings.window_position = self.get_position()
        settings.window_maximized = self.is_maximized()

    def restore_state(self):
        """Restore the window's state."""
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

    def _build_widgets(self):
        """Build main window widgets."""
        # HeaderBar
        header_bar = HeaderBar.get_default()
        header_bar.select_btn.connect("clicked", Window.toggle_select)
        header_bar.add_btn.connect("clicked", self.add_account)
        header_bar.cancel_btn.connect("clicked", Window.toggle_select)
        self.set_titlebar(header_bar)

        # Main Container
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Main Stack
        self.main_stack = Gtk.Stack()

        # Accounts List
        account_list_cntr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        accounts_widget = AccountsWidget.get_default()
        accounts_widget.connect("changed", self.update_view)

        # Search Bar
        self.search_bar = SearchBar()
        self.search_bar.search_button = header_bar.search_btn
        self.search_bar.search_list = accounts_widget.accounts_lists

        # Actions Bar
        actions_bar = ActionsBar.get_default()
        actions_bar.delete_btn.connect("clicked",
                                       self.__on_delete_clicked)
        accounts_widget.connect("selected-rows-changed",
                                actions_bar.on_selected_rows_changed)

        account_list_cntr.pack_start(self.search_bar, False, False, 0)
        account_list_cntr.pack_start(accounts_widget, True, True, 0)
        account_list_cntr.pack_start(actions_bar, False, False, 0)

        self.main_stack.add_named(account_list_cntr,
                                  "accounts-list")

        # Empty accounts list
        self.main_stack.add_named(EmptyAccountsList.get_default(),
                                  "empty-accounts-list")
        login_widget = LoginWidget.get_default()
        login_widget.login_btn.connect("clicked", self.__on_unlock)
        self.main_stack.add_named(login_widget, "login")

        self.main_container.pack_start(self.main_stack, True, True, 0)
        self.add(self.main_container)
        self.update_view()

        actions_bar.bind_property("visible", header_bar.cancel_btn,
                                  "visible",
                                  GObject.BindingFlags.BIDIRECTIONAL)
        actions_bar.bind_property("no_show_all", header_bar.cancel_btn,
                                  "no_show_all",
                                  GObject.BindingFlags.BIDIRECTIONAL)

    def _on_account_delete(self, *_):
        Window.toggle_select()
        self.update_view()

    def __on_delete_clicked(self, *__):
        notification = Gd.Notification()
        accounts_widget = AccountsWidget.get_default()
        notification.connect("dismissed", accounts_widget.delete_selected)
        notification.set_timeout(5)
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        notification_lbl = Gtk.Label()
        notification_lbl.set_text(_("An account or more were removed."))
        container.pack_start(notification_lbl, False, False, 3)

        undo_btn = Gtk.Button()
        undo_btn.set_label(_("Undo"))
        undo_btn.connect("clicked", lambda widget: notification.hide())
        container.pack_end(undo_btn, False, False, 3)

        notification.add(container)
        accounts_widget.add(notification)
        accounts_widget.reorder_child(notification, 1)
        accounts_widget.show_all()

    def __on_locked(self, *_):
        if self.key_press_signal:
            self.disconnect(self.key_press_signal)
        HeaderBar.get_default().set_state(HeaderBarState.LOCKED)
        child = self.main_stack.get_child_by_name("login")
        child.show_all()
        self.main_stack.set_visible_child(child)

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
