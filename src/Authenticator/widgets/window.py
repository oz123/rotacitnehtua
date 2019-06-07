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
from gi.repository import Gtk, GObject, Gio, Handy

from Authenticator.models import Logger, Settings, AccountsManager
from Authenticator.widgets.accounts.add import AddAccountWindow
from Authenticator.widgets.accounts.list import AccountsWidget


class WindowView:
    NORMAL = 0
    LOCKED = 1
    EMPTY = 2


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/window.ui')
class Window(Gtk.ApplicationWindow):
    """Main Window object."""
    __gtype_name__ = 'Window'

    # Default Window instance
    instance: 'Window' = None

    view = GObject.Property(type=int, default=0)

    search_btn: Gtk.ToggleButton = Gtk.Template.Child()
    primary_menu_btn: Gtk.MenuButton = Gtk.Template.Child()

    main_stack: Gtk.Stack = Gtk.Template.Child()
    headerbar_stack: Gtk.Stack = Gtk.Template.Child()
    accounts_stack: Gtk.Stack = Gtk.Template.Child()

    search_bar: Handy.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    password_entry: Gtk.Entry = Gtk.Template.Child()

    def __init__(self):
        super(Window, self).__init__()
        self.init_template('Window')

        self.connect("notify::view", self.__state_changed)

        self.key_press_signal = None
        self.restore_state()
        # Start the Account Manager
        AccountsManager.get_default()

        self.__init_widgets()

    @staticmethod
    def get_default() -> 'Window':
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
            add_window.set_size_request(*self.get_size())
            add_window.resize(*self.get_size())
            add_window.show_all()
            add_window.present()

    def set_menu(self, menu: Gio.Menu):
        popover = Gtk.Popover.new_from_model(self.primary_menu_btn, menu)

        def primary_menu_btn_handler(_, popover):
            popover.set_visible(not popover.get_visible())

        self.primary_menu_btn.connect('clicked', primary_menu_btn_handler, popover)

    def toggle_search(self, *_):
        """
            Switch the state of the search mode

            Switches the state of the search mode if:
                - The application is not locked
                - There are at least one account in the database
            return: None
        """
        if self.props.view == WindowView.NORMAL:
            toggled = not self.search_btn.props.active
            self.search_btn.set_property("active", toggled)

    def refresh_view(self, *_):
        if AccountsManager.get_default().props.empty:
            self.props.view = WindowView.EMPTY
        else:
            self.props.view = WindowView.NORMAL

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
        accounts_widget.connect("account-removed", self.refresh_view)
        accounts_widget.connect("account-added", self.refresh_view)
        self.accounts_stack.add_named(accounts_widget, "accounts")
        self.accounts_stack.set_visible_child_name("accounts")

        AccountsManager.get_default().connect("notify::empty", self.refresh_view)

        self.search_bar.connect_entry(self.search_entry)
        self.search_bar.bind_property("search-mode-enabled", self.search_btn,
                                      "active",
                                      GObject.BindingFlags.BIDIRECTIONAL)

    def __add_action(self, key: str, callback, prop_bind: str = None,
                     bind_flag=GObject.BindingFlags.INVERT_BOOLEAN):
        action = Gio.SimpleAction.new(key, None)
        action.connect("activate", callback)
        if prop_bind:
            self.bind_property(prop_bind, action, "enabled", bind_flag)
        self.add_action(action)

    def __state_changed(self, *_):
        if self.props.view == WindowView.LOCKED:
            visible_child = "locked_state"
            visible_headerbar = "locked_headerbar"
            if self.key_press_signal:
                self.disconnect(self.key_press_signal)
        else:
            if self.props.view == WindowView.EMPTY:
                visible_child = "empty_state"
                visible_headerbar = "empty_headerbar"
            else:
                visible_child = "normal_state"
                visible_headerbar = "main_headerbar"
                # Connect on type search bar
                self.key_press_signal = self.connect("key-press-event",
                                                     lambda x, y: self.search_bar.handle_event(y))
        self.main_stack.set_visible_child_name(visible_child)
        self.headerbar_stack.set_visible_child_name(visible_headerbar)

    @Gtk.Template.Callback('unlock_btn_clicked')
    def __unlock_btn_clicked(self, *_):
        from Authenticator.models import Keyring
        typed_password = self.password_entry.get_text()
        if typed_password == Keyring.get_default().get_password():
            self.get_application().set_property("is-locked", False)
            # Reset password entry
            self.password_entry.get_style_context().remove_class("error")
            self.password_entry.set_text("")
        else:
            self.password_entry.get_style_context().add_class("error")

    @Gtk.Template.Callback('search_changed')
    def __search_changed(self, entry: Gtk.SearchEntry):
        """
            Handles search-changed signal.
        """
        def filter_func(row, data, *_):
            """
                Filter function
            """
            data = data.lower()
            if len(data) > 0:
                username = row.account.username.lower()
                provider_name = row.account.provider.name.lower()
                return (
                    data in username or data in provider_name
                )
            else:
                return True
        data = entry.get_text().strip()
        search_lists = AccountsWidget.get_default().accounts_lists
        results_count = 0
        for search_list in search_lists:
            search_list.set_filter_func(filter_func,
                                        data, False)
            for elem in search_list:

                if elem.get_child_visible():
                    results_count += 1

        if results_count == 0:
            self.accounts_stack.set_visible_child_name("empty_results")
        else:
            self.accounts_stack.set_visible_child_name("accounts")
