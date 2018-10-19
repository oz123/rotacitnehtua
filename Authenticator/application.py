"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distr  ibuted in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from gettext import gettext as _

from gi import require_version

require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
from .widgets import Window, AboutDialog, import_json, export_json, import_pgp_json, export_pgp_json
from .models import Settings, Clipboard, Logger


class Application(Gtk.Application):
    """Authenticator application object."""
    instance = None
    USE_QRSCANNER = True
    IS_DEVEL = False
    is_locked = GObject.Property(type=bool, default=False)

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id="com.github.bilelmoussaoui.Authenticator",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_("Authenticator"))
        GLib.set_prgname("Authenticator")
        self.connect("notify::is-locked", self.__is_locked_changed)
        self.alive = True
        Settings.get_default().bind("is-locked", self, "is_locked", Gio.SettingsBindFlags.GET)
        self._menu = Gio.Menu()

    def __is_locked_changed(self, *_):
        if self.is_locked:
            Window.get_default().emit("locked")
        else:
            Window.get_default().emit("unlocked")

    @staticmethod
    def get_default():
        if Application.instance is None:
            Application.instance = Application()
        return Application.instance

    def do_startup(self):
        """Startup the application."""
        Gtk.Application.do_startup(self)
        # Unlock the keyring
        self.__generate_menu()
        self.__setup_actions()
        self.set_property("is-locked", Settings.get_default().can_be_locked)
        Application.__setup_css()

        # Set the default night mode
        is_night_mode = Settings.get_default().is_night_mode
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-application-prefer-dark-theme",
                                  is_night_mode)

    @staticmethod
    def __setup_css():
        """Setup the CSS and load it."""
        uri = 'resource:///com/github/bilelmoussaoui/Authenticator/style.css'
        provider_file = Gio.File.new_for_uri(uri)
        provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        provider.load_from_file(provider_file)
        context.add_provider_for_screen(screen, provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
        Gtk.IconTheme.get_default().add_resource_path("/com/github/bilelmoussaoui/Authenticator")
        Logger.debug("Loading CSS")

    def __generate_menu(self):
        """Generate application menu."""
        # Lock/Unlock
        if Settings.get_default().can_be_locked:
            lock_content = Gio.Menu.new()
            lock_content.append_item(Gio.MenuItem.new(_("Lock the application"), "app.lock"))
            self._menu.append_item(Gio.MenuItem.new_section(None, lock_content))

        # Backup
        backup_content = Gio.Menu.new()
        import_menu = Gio.Menu.new()
        export_menu = Gio.Menu.new()

        import_menu.append_item(Gio.MenuItem.new(_("from a plain-text JSON file"), "app.import_json"))
        import_menu.append_item(Gio.MenuItem.new(_("from an OpenPGP-encrypted JSON file"), "app.import_pgp_json"))
        export_menu.append_item(Gio.MenuItem.new(_("in a plain-text JSON file"), "app.export_json"))
        export_menu.append_item(Gio.MenuItem.new(_("in an OpenPGP-encrypted JSON file"), "app.export_pgp_json"))

        backup_content.insert_submenu(0, _("Restore"), import_menu)
        backup_content.insert_submenu(1, _("Backup"), export_menu)

        backup_section = Gio.MenuItem.new_section(None, backup_content)
        self._menu.append_item(backup_section)

        # Main section
        main_content = Gio.Menu.new()
        # Night mode action
        main_content.append_item(Gio.MenuItem.new(_("Settings"), "app.settings"))
        main_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        main_content.append_item(Gio.MenuItem.new(_("Keyboard Shortcuts"), "app.shortcuts"))
        help_section = Gio.MenuItem.new_section(None, main_content)
        self._menu.append_item(help_section)

    def __setup_actions(self):
        self.__add_action("about", self.__on_about)
        self.__add_action("shortcuts", self.__on_shortcuts)
        self.__add_action("quit", self.__on_quit)
        self.__add_action("settings", self.__on_settings, "is_locked")
        self.__add_action("import_json", self.__on_import_json, "is_locked")
        self.__add_action("import_pgp_json", self.__on_import_pgp_json, "is_locked")
        self.__add_action("export_json", self.__on_export_json, "is_locked")
        self.__add_action("export_pgp_json", self.__on_export_pgp_json, "is_locked")
        if Settings.get_default().can_be_locked:
            self.__add_action("lock", self.__on_lock, "is_locked")

    def __add_action(self, key, callback, prop_bind=None, bind_flag=GObject.BindingFlags.INVERT_BOOLEAN):
        action = Gio.SimpleAction.new(key, None)
        action.connect("activate", callback)
        if prop_bind:
            self.bind_property(prop_bind, action, "enabled", bind_flag)
        self.add_action(action)

    def do_activate(self, *_):
        """On activate signal override."""
        window = Window.get_default()

        window.set_application(self)
        window.set_menu(self._menu)
        window.connect("delete-event", lambda x, y: self.__on_quit())
        if Application.IS_DEVEL:
            window.get_style_context().add_class("devel")
        self.add_window(window)
        window.show_all()
        window.present()

    def __on_lock(self, *_):
        self.set_property("is-locked", True)

    @staticmethod
    def __on_about(*_):
        """
            Shows about dialog
        """
        dialog = AboutDialog()
        dialog.set_transient_for(Window.get_default())
        dialog.run()
        dialog.destroy()

    def __on_shortcuts(self, *_):
        builder = Gtk.Builder()
        builder.add_from_resource("/com/github/bilelmoussaoui/Authenticator/Shortcuts.ui")
        dialog = builder.get_object("shortcuts")
        dialog.set_transient_for(Window.get_default())
        dialog.show()

    @staticmethod
    def __on_import_json(*_):
        from .models import BackupJSON
        filename = import_json(Window.get_default())
        if filename:
            BackupJSON.import_file(filename)
        Window.get_default().update_view()

    @staticmethod
    def __on_export_json(*_):
        from .models import BackupJSON
        filename = export_json(Window.get_default())
        if filename:
            BackupJSON.export_file(filename)

    @staticmethod
    def __on_import_pgp_json(*_):
        from .widgets import GPGRestoreWindow
        filename = import_pgp_json(Window.get_default())
        if filename:
            gpg_window = GPGRestoreWindow(filename)
            gpg_window.set_transient_for(Window.get_default())
            gpg_window.show_all()

    @staticmethod
    def __on_export_pgp_json(*_):
        from .models import BackupPGPJSON
        filename = export_pgp_json(Window.get_default())
        if filename:
            def export_pgp(_, fingerprint):
                BackupPGPJSON.export_file(filename, fingerprint)

            from .widgets.backup import FingprintPGPWindow
            fingerprint_window = FingprintPGPWindow(filename)
            fingerprint_window.set_transient_for(Window.get_default())
            fingerprint_window.connect("selected", export_pgp)
            fingerprint_window.show_all()

    @staticmethod
    def __on_settings(*_):
        from .widgets import SettingsWindow
        settings_window = SettingsWindow()
        settings_window.present()
        settings_window.show_all()

    def __on_quit(self, *_):
        """
        Close the application, stops all threads
        and clear clipboard for safety reasons
        """
        Clipboard.clear()
        Window.get_default().close()
        self.quit()

