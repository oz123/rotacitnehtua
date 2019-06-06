"""
Empty uneeded provider iamges
"""
from os import path
from yoyo import step

__depends__ = {'authenticator_20190525_04_Faezz-restore-old-accounts'}


def do_step(conn):

    providers_db = conn.execute("SELECT id, image FROM providers").fetchall()

    to_empty = []
    for provider_id, provider_image in providers_db:
        if provider_image and path.basename(provider_image) == provider_image:
            to_empty.append(str(provider_id))

    if len(to_empty):
        providers_ids = ", ".join(to_empty)
        conn.execute("UPDATE providers SET image='' WHERE id IN (?)", (providers_ids, ))


steps = [
    step(do_step, ignore_errors='apply')
]
