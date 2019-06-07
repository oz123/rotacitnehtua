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
from pathlib import Path
from enum import Enum
from tempfile import NamedTemporaryFile
import asyncio
from pyfavicon import Favicon
import concurrent
from Authenticator.models import Provider


class ProviderImageState(Enum):
    FOUND = 0
    NOT_FOUND = 1
    LOADING = 2

    @property
    def stack_name(self):
        if self.value == 0:
            return "provider_image"
        elif self.value == 1:
            return "provider_not_found"
        else:
            return "provider_loading"


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/provider_image.ui')
class ProviderImage(Gtk.Stack):
    """
        An Object that represents the provider service's image

        It contains a Gtk.Spinner and a Gtk.Image inside a Gtk.Stack
        It shows the Spinner when the provider image is being downloaded,
        once the download was successful, we show that image
    """
    __gtype_name__ = 'ProviderImage'

    __gsignals__ = {
        'provider-changed': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT, )
        ),
        'image-downloaded': (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str, GObject.TYPE_PYOBJECT, )
        )
    }

    provider_image = Gtk.Template.Child()
    provider_spinner = Gtk.Template.Child()
    image_eventbox = Gtk.Template.Child()
    insert_image = Gtk.Template.Child()
    not_found_box = Gtk.Template.Child()

    _timeout_id = 0
    CACHE_DIR = path.join(GLib.get_user_cache_dir(), "Authenticator")

    def __init__(self, provider=None, image_size=48):
        super(ProviderImage, self).__init__()
        self.init_template('ProviderImage')
        self.provider = provider if provider else Provider()

        self.image_size = image_size

        self._build_widget()

    def _build_widget(self):
        self.set_state(ProviderImageState.NOT_FOUND)
        self.not_found_box.props.width_request = self.image_size
        self.not_found_box.props.height_request = self.image_size
        self.provider_image.set_pixel_size(self.image_size)

        self.connect("provider-changed", self.__on_provider_changed)

        def set_show_insert_image(state):
            if state != self.insert_image.get_visible():
                self.insert_image.set_visible(state)
                self.insert_image.set_no_show_all(not state)

        self.image_eventbox.connect("enter-notify-event",
                                    lambda *_: set_show_insert_image(True))
        self.image_eventbox.connect("leave-notify-event",
                                    lambda *_: set_show_insert_image(False))

        if self.provider.image:
            if not self.set_image(self.provider.image) and self.provider.website:
                self.fetch_favicon_from_url(self.provider.website)

    def set_state(self, state: ProviderImageState):
        self.state = state
        if state == ProviderImageState.LOADING:
            self.provider_spinner.start()
        else:
            self.provider_spinner.stop()
        self.set_visible_child_name(state.stack_name)

    @property
    def image(self):
        if self.provider:
            return self.provider.image
        return None

    def set_image(self, image):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image)
            pixbuf = pixbuf.scale_simple(self.image_size, self.image_size,
                                         GdkPixbuf.InterpType.BILINEAR)
            self.provider_image.set_from_pixbuf(pixbuf)
            self.set_state(ProviderImageState.FOUND)
            return True
        except GLib.Error:
            pass
        self.set_state(ProviderImageState.NOT_FOUND)
        return False

    # Callbacks
    @Gtk.Template.Callback('select_image_clicked')
    def __on_select_image_clicked(self, *args):
        dialog = Gtk.FileChooserNative()
        dialog.set_action(Gtk.FileChooserAction.OPEN)
        dialog.set_transient_for(self.get_toplevel())

        # Allow to select images only

        mimes = ('image/jpeg', 'image/png', 'image/svg+xml')
        for mime_type in mimes:
            img_filter = Gtk.FileFilter()
            img_filter.set_name(mime_type)
            img_filter.add_mime_type(mime_type)
            dialog.add_filter(img_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            file_uri = dialog.get_uri()
            cache_file = self.__create_cache_file(file_uri)
            self.set_image(cache_file)
        dialog.destroy()

    # Signals

    def __on_provider_changed(self, _, provider):
        self.provider = provider
        self.provider_spinner.start()
        self.set_state(ProviderImageState.LOADING)
        if provider.image:  # If we have already an image in the database
            if path.exists(provider.image):
                self.set_image(provider.image)
            elif provider.website:
                self.fetch_favicon_from_url(provider.website)
            else:
                self.provider.update(image=None)
                self.set_state(ProviderImageState.NOT_FOUND)
        elif provider.website:  # If we can download a favicon
            self.fetch_favicon_from_url(provider.website)
        else:
            self.set_state(ProviderImageState.NOT_FOUND)

    def fetch_favicon_from_url(self, provider_website):
        if provider_website:
            worker_loop = asyncio.new_event_loop()
            pool = concurrent.futures.ThreadPoolExecutor()
            current_provider = self.provider
            pool.submit(self._download_favicon, worker_loop, provider_website,
                        current_provider)

    # Private
    def _download_favicon(self, loop, provider_website, current_provider):
        cache_dir = Path(ProviderImage.CACHE_DIR)
        if not cache_dir.exists():
            cache_dir.mkdir()

        async def fetch_favicon():
            favicon = Favicon(download_dir=cache_dir)
            icons = await favicon.from_url(provider_website)
            largest_icon = icons.get_largest()
            if largest_icon:
                await largest_icon.save()
                GLib.idle_add(self.emit, "image-downloaded", largest_icon.path,
                              current_provider)
            else:
                self.set_state(ProviderImageState.NOT_FOUND)
        # Hackish solution for https://github.com/python/cpython/pull/13548
        loop.set_exception_handler(lambda loop, ctx: None)
        loop.run_until_complete(fetch_favicon())

    def __create_cache_file(self, file_uri):
        """
            Store a copy of the image under the cache dir of Authenticator.
        """
        gfile = Gio.File.new_for_uri(file_uri)
        # Copy file to cache dir
        cache_filename = path.basename(NamedTemporaryFile().name)
        destination_file = path.join(ProviderImage.CACHE_DIR, cache_filename)
        dfile = Gio.File.new_for_path(destination_file)
        gfile.copy(dfile, Gio.FileCopyFlags.NONE, None, None, None)

        self.set_image(destination_file)
        return destination_file

    def do_image_downloaded(self, image_path, provider):

        if image_path and path.exists(image_path):
            if provider:
                provider.update(image=image_path)  # Update the database
            # If the user didn't change the provider while downloading
            if provider.provider_id == self.provider.provider_id:
                self.set_image(image_path)
                self.set_state(ProviderImageState.FOUND)
            return
        self.set_state(ProviderImageState.NOT_FOUND)
