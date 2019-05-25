"""
Add default providers
"""
from gi.repository import Gio
from yoyo import step
import json
__depends__ = {'authenticator_20190525_02_mdR2o-create-table-providers'}


def do_step(conn):
    uri = 'resource:///com/github/bilelmoussaoui/Authenticator/data.json'
    g_file = Gio.File.new_for_uri(uri)
    content = str(g_file.load_contents(None)[1].decode("utf-8"))
    data = json.loads(content)
    providers = []
    for provider_name, provider_info in data.items():
        providers.append((provider_name, provider_info['url'],
                          provider_info['doc'], provider_info['img'],))
    query = "INSERT INTO providers (name, website, doc_url, image) VALUES (?, ?, ?, ?)"
    conn.executemany(query, providers)
    conn.commit()


steps = [
    step(do_step, ignore_errors='apply')
]
