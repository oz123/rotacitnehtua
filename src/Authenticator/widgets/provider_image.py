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

from gi.repository import Gtk, GObject, GdkPixbuf, GLib, Gio
from os import path
from tempfile import NamedTemporaryFile
from gettext import gettext as _

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
    provider_set_image_box = Gtk.Template.Child()
    _image_path = None

    provider = GObject.Property(type=str)


    def __init__(self, provider_name, image_path, image_size, allow_setting_image=False):
        super(ProviderImage, self).__init__()
        self.init_template('ProviderImage')
        self._image_path = image_path
        self.allow_setting_image = allow_setting_image
        if not allow_setting_image:
            self.remove(self.provider_set_image_box)
        self.connect("notify::provider", self.__on_provider_changed)
        self.image_size = image_size
        self.provider = provider_name
        self.provider_image.set_pixel_size(image_size)

    def get_path(self):
        return self._image_path

    def __on_provider_changed(self, _, provider):
        self.provider_spinner.start()
        self.set_visible_child_name("provider_spinner")

        provider = ProviderManager.get_default().get_by_name(
            self.get_property('provider')
        )
        if provider and not isinstance(provider, str):
            FaviconManager.get_default().grab_favicon(provider.img, provider.url,
                                                      self.__on_favicon_downloaded)
        elif self._image_path is not None:
            self.__on_favicon_downloaded(self._image_path)
        else:
            self.set_visible_child_name("provider_image_not_found")

    def __on_favicon_downloaded(self, img_path):
        self.provider_spinner.stop()
        try:
            if img_path and path.exists(img_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(img_path, self.image_size, self.image_size)

                if pixbuf and (pixbuf.props.width != self.image_size or pixbuf.props.height != self.image_size):
                    pixbuf = pixbuf.scale_simple(self.image_size, self.image_size,
                                                GdkPixbuf.InterpType.BILINEAR)
                self.provider_image.set_from_pixbuf(pixbuf)
                self.set_visible_child_name("provider_image")
        except GLib.Error:
            if self.allow_setting_image:
                self.set_visible_child_name("provider_image_not_found")
            else:
                self.provider_image.set_from_resource("/com/github/bilelmoussaoui/Authenticator/authenticator.svg")
                self.set_visible_child_name("provider_image")

    @Gtk.Template.Callback('select_image_clicked')
    def __on_select_image_clicked(self, *args):
        dialog = Gtk.FileChooserNative()
        dialog.set_action(Gtk.FileChooserAction.OPEN)
        response = dialog.run()

        # Allow to select images only
        images_filter = Gtk.FileFilter()
        mimes = ('image/jpeg', 'image/png', 'image/svg+xml')
        for mime_type in mimes:
            images_filter.set_name(mime_type)
            images_filter.add_mime_type(mime_type)
        dialog.add_filter(images_filter)

        if response == Gtk.ResponseType.ACCEPT:
            file_uri = dialog.get_uri()
            cache_file = self.__create_cache_file(file_uri)
            self._image_path = cache_file
            self.__on_favicon_downloaded(cache_file)
        dialog.destroy()


    def __create_cache_file(self, file_uri):
        """
            Store a copy of the image under the cache dir of Authenticator.
        """
        gfile = Gio.File.new_for_uri(file_uri)
        # Copy file to cache dir
        cache_filename = path.basename(NamedTemporaryFile().name)
        destination_file = path.join(FaviconManager.CACHE_DIR, cache_filename)
        dfile = Gio.File.new_for_path(destination_file)
        gfile.copy(dfile, Gio.FileCopyFlags.NONE, None, None, None)

        self.__on_favicon_downloaded(destination_file)
        return destination_file
