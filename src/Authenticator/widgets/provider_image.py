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

from gi.repository import Gtk, GObject, GdkPixbuf, GLib
from os import path


from Authenticator.models import ProviderManager, FaviconManager


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/provider_image.ui')
class ProviderImage(Gtk.Stack):
    """
        An Object that represents the provider service's image

        It contains a Gtk.Spinner and a Gtk.Image inside a Gtk.Stack
        It shows the Spinner when the provider image is being downloaded,
        once the download was successful, we show that image
    """

    __gtype_name__ = 'ProviderImage'

    provider_image = Gtk.Template.Child()
    provider_spinner = Gtk.Template.Child()

    provider = GObject.Property(type=str)

    def __init__(self, provider_name, image_size):
        super(ProviderImage, self).__init__()
        self.init_template('ProviderImage')

        self.connect("notify::provider", self.__on_provider_changed)
        self.image_size = image_size
        self.provider = provider_name
        self.provider_image.set_pixel_size(image_size)


    def __on_provider_changed(self, _, provider):
        self.provider_spinner.start()
        self.set_visible_child_name("provider_spinner")

        provider = ProviderManager.get_default().get_by_name(
            self.get_property('provider')
        )
        if provider:
            FaviconManager.get_default().grab_favicon(provider.img, provider.url,
                                                      self.__on_favicon_downloaded)
        else:
            self.__on_favicon_downloaded(None)

    def __on_favicon_downloaded(self, img_path):

        try:
            if img_path and path.exists(img_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, self.image_size, self.image_size)

                if pixbuf and (pixbuf.props.width != self.image_size or pixbuf.props.height != self.image_size):
                    pixbuf = pixbuf.scale_simple(self.image_size, self.image_size,
                                                GdkPixbuf.InterpType.BILINEAR)
                self.provider_image.set_from_pixbuf(pixbuf)
        except GLib.Error:
            self.provider_image.set_from_resource("/com/github/bilelmoussaoui/Authenticator/authenticator.svg")
        self.provider_spinner.stop()
        self.set_visible_child_name("provider_image")
