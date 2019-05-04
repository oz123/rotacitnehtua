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
from collections import namedtuple
import json
from gi.repository import Gio

class ProviderManager:

    instance = None
    __providers = []

    def __init__(self):
        self.__parse_providers()

    @staticmethod
    def get_default():
        if ProviderManager.instance is None:
            ProviderManager.instance = ProviderManager()
        return ProviderManager.instance

    @property
    def providers(self):
        return self.__providers

    def get_by_name(self, provider_name):
        if not provider_name:
            return
        for provider in self.providers:
            _current_name = str(provider.name)
            if _current_name.lower().strip() == provider_name.lower().strip():
                return provider
        return None

    def __parse_providers(self):
        uri = 'resource:///com/github/bilelmoussaoui/Authenticator/data.json'
        g_file = Gio.File.new_for_uri(uri)
        content = str(g_file.load_contents(None)[1].decode("utf-8"))
        data = json.loads(content)
        Provider = namedtuple('Provider', 'name img url doc')
        for provider_name, provider_info in data.items():
            provider = Provider(provider_name, provider_info['img'],
                                provider_info['url'], provider_info['doc'])
            self.__providers.append(provider)
    
