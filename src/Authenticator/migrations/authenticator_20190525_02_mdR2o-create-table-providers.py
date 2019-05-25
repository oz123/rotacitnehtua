"""
Create table providers
"""

from yoyo import step

__depends__ = {'authenticator_20190525_01_GdUDU-create-table-accounts'}

steps = [
    step(
        '''CREATE TABLE "providers" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            "name" VARCHAR NOT NULL,
            "website" VARCHAR NULL,
            "doc_url" VARCHAR NULL,
            "image" VARCHAR NULL
        )
        ''',
        'DROP TABLE "providers"',
        ignore_errors='apply'
    )
]
