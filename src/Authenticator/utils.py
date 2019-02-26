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
from os import environ, path
from gi.repository import Gtk, GdkPixbuf, GLib

def load_pixbuf_from_provider(provider_logo, size=48):
    if provider_logo and path.exists(provider_logo):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(provider_logo, size, size)
        except GLib.Error:
            pass

    theme = Gtk.IconTheme.get_default()
    theme.add_resource_path("/com/github/bilelmoussaoui/Authenticator")
    pixbuf = theme.load_icon("authenticator-symbolic", size, 0)
    if pixbuf and (pixbuf.props.width != size or pixbuf.props.height != size):
        pixbuf = pixbuf.scale_simple(size, size,
                                        GdkPixbuf.InterpType.BILINEAR)
    return pixbuf

