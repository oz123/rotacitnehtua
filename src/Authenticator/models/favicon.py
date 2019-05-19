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
from os import path, mkdir
from bs4 import BeautifulSoup
import gi
gi.require_version('Soup', '2.4')
from gi.repository import Gio, GLib, Soup
from urllib.parse import urlparse
import base64
import requests
from threading import Thread

LINK_RELS = [
    'icon',
    'shortcut icon',
    'apple-touch-icon',
    'apple-touch-icon-precomposed',
    'fluid-icon'
]

class FaviconManager:

    instance = None
    CACHE_DIR = path.join(GLib.get_user_cache_dir(), "Authenticator")

    def __init__(self):
        """
            Start a new FaviconManager.
        """
        pass

    def grab_favicon(self, img, url, callback=None):

        # Create the cache directory
        if not path.isdir(FaviconManager.CACHE_DIR):
            mkdir(FaviconManager.CACHE_DIR)

        img_path = path.join(FaviconManager.CACHE_DIR, img)
        if not path.isfile(img_path):
            self.__download_favicon(url, img_path, callback)
        else:
            # If the file was downloaded before, just load it
            callback(img_path)

    def __download_favicon(self, url, img_path, callback=None):
        """
            Get the website favicon and save it.
        """
        r = requests.get(url, headers= {'DNT': '1'})
        if r.status_code == 200:
           self.__on_download_finished(r.url, r.text, img_path, callback)

    def __on_download_finished(self, provider_url, html_content, img_path, callback=None):
        favicon_url = self.__grab_favicon_url(html_content, provider_url)
        if favicon_url:
            # If the favicon is not a base64 png image
            if "base64" in favicon_url:
                favicon = base64.b64decode(favicon_url.split("base64,")[-1])
                with open(img_path, 'wb') as favicon_obj:
                    favicon_obj.write(favicon)
                callback(img_path, data)
            else:
                self.__save_favicon(favicon_url, img_path, callback)
        return None

    def __get_largest_icon(self, links):
        largest = (links[0], 0)
        for link in links:
            size = link.attrs.get('sizes', '').split("x")
            try:
                size = int(size[0])
                if size > largest[1]:
                    largest = (link, size)
            except Exception:
                pass
        return largest[0]

    def __grab_favicon_url(self, html_content, url):
        bsoup = BeautifulSoup(html_content, features="html.parser")
        links = []
        for rel in LINK_RELS:
            links.extend(bsoup.find_all('link', attrs={'rel': rel, 'href': True}))
        if len(links):
            largest_icon = self.__get_largest_icon(links)
            if largest_icon:
                favicon_url = largest_icon.attrs['href']
                if not favicon_url.startswith("http") \
                    and not favicon_url.startswith("www") \
                    and not favicon_url.startswith("https") \
                    and not favicon_url.startswith("//"):
                    favicon_url = url.rstrip('/') + '/' + favicon_url.lstrip('/')
                elif favicon_url.startswith("//"):
                    url_obj = urlparse(url)
                    favicon_url = url_obj.scheme + '://' + favicon_url.lstrip('/')
                return favicon_url
        return None

    def __save_favicon(self, favicon_url, img_path, callback=None):
        if favicon_url:
            try:
                r = requests.get(favicon_url, stream=True)
                if r.status_code == 200:
                    with open(img_path, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128):
                            fd.write(chunk)
                    callback(img_path)
            except requests.exceptions.ConnectionError:
                # In case the favicon is not on the server anymore
                pass
        return None
