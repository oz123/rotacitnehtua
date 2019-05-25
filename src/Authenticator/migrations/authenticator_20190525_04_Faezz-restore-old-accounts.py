"""
Restore old accounts
"""

from yoyo import step

__depends__ = {'authenticator_20190525_03_R7miN-add-default-providers'}


def do_step(conn):
    accounts = conn.execute("SELECT * FROM accounts").fetchall()
    _accounts = []

    providers_db = conn.execute("SELECT id, name FROM providers").fetchall()
    providers = {}
    for provider_id, provider_name in providers_db:
        providers[provider_name] = provider_id
    cursor = conn.cursor()
    for account_id, username, provider_name, secret_id in accounts:
        if provider_name not in providers.keys():
            cursor.execute("INSERT INTO providers (name) VALUES (?)", (provider_name, ))
            provider_id = cursor.lastrowid
        else:
            provider_id = providers[provider_name]
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
