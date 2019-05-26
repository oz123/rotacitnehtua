"""
Restore old accounts
"""

from yoyo import step
from collections import OrderedDict

__depends__ = {'authenticator_20190525_03_R7miN-add-default-providers'}


def do_step(conn):
    # atler columns from secret id to token_id before
    # to fix the issue on older db
    try:
        accounts = conn.execute("SELECT id, username, token_id, provider FROM accounts").fetchall()
    except Exception:
        accounts = conn.execute("SELECT id, username, secret_id, provider FROM accounts").fetchall()
    _accounts = []

    providers_db = conn.execute("SELECT id, name FROM providers").fetchall()
    providers = OrderedDict()
    for provider_id, provider_name in providers_db:
        providers[provider_id] = provider_name.lower()
    cursor = conn.cursor()

    for account_id, username, secret_id, provider in accounts:
        if isinstance(provider, str):
            if provider.lower() not in providers.values():
                cursor.execute("INSERT INTO providers (name) VALUES (?)", (provider, ))
                provider_id = cursor.lastrowid
            else:
                provider_index = list(providers.values()).index(provider.lower())
                provider_id = list(providers.keys())[provider_index]
        else:
            provider_id = provider
        _accounts.append((account_id, username, provider_id, secret_id))

    cursor.execute(" ALTER TABLE accounts RENAME TO tmp;")
    cursor.execute(''' CREATE TABLE "accounts" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    "username" VARCHAR NOT NULL,
                    "token_id" VARCHAR NOT NULL UNIQUE,
                    "provider" INTEGER NOT NULL
                    )''')
    cursor.execute("DROP TABLE tmp;")
    added_tokens = []
    for account_id, username, provider_id, token_id in _accounts:
        if token_id not in added_tokens:
            cursor.execute("INSERT INTO accounts (username, provider, token_id) VALUES (?, ?, ?)", (username, provider_id, token_id))
            added_tokens.append(token_id)


steps = [
    step(do_step, ignore_errors='apply')
]
