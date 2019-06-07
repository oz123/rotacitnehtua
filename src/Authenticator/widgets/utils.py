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
from gi.repository import Gtk

__all__ = ['import_json', 'export_json']


def import_json(parent: Gtk.Window) -> str:
    mimetype = {'type': "application/json", 'name': _("JSON files")}
    return __open_file_chooser(parent, mimetype)


def export_json(parent: Gtk.Window) -> str:
    mimetype = {'type': "application/json", 'name': _("JSON files")}
    return __open_file_chooser(parent, mimetype, Gtk.FileChooserAction.SAVE)


def __open_file_chooser(parent: Gtk.Window, mimetype: dict,
                        action=Gtk.FileChooserAction.OPEN) -> str:
    file_chooser = Gtk.FileChooserNative()
    file_chooser.set_action(action)
    file_chooser.set_transient_for(parent)
    filter_json = Gtk.FileFilter()
    filter_json.set_name(mimetype["name"])
    filter_json.add_mime_type(mimetype["type"])
    file_chooser.add_filter(filter_json)
    response = file_chooser.run()
    uri = None
    if response == Gtk.ResponseType.ACCEPT:
        uri = file_chooser.get_uri()
    file_chooser.destroy()
    return uri
