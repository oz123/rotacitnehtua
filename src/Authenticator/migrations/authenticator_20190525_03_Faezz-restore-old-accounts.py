"""
Restore old accounts
"""

from yoyo import step

__depends__ = {'authenticator_20190525_02_mdR2o-create-table-providers'}


def do_step(conn):
    accounts = conn.execute("SELECT * FROM accounts").fetchall()
    _accounts = []
    cursor = conn.cursor()
    for account_id, username, provider_name, secret_id in accounts:
        cursor.execute("INSERT INTO providers (name) VALUES (?)", (provider_name, ))
        provider_id = cursor.lastrowid
        _accounts.append((account_id, username, provider_id, secret_id))

    cursor.execute(" ALTER TABLE accounts RENAME TO tmp;")
    cursor.execute(''' CREATE TABLE "accounts" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    "username" VARCHAR NOT NULL,
                    "token_id" VARCHAR NOT NULL UNIQUE,
                    "provider" INTEGER NOT NULL
                    )''')
    cursor.execute("DROP TABLE tmp;")
    for account_id, username, provider_id, token_id in _accounts:
        cursor.execute("INSERT INTO accounts (username, provider, token_id) VALUES (?, ?, ?)", (username, provider_id, token_id))


steps = [
    step(do_step, ignore_errors='apply')
]
