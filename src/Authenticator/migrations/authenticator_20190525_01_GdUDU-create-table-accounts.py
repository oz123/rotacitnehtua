"""
Create table accounts
"""

from yoyo import step

__depends__ = {}

steps = [
    step('''
         CREATE TABLE "accounts" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            "username" VARCHAR NOT NULL,
            "provider" VARCHAR NOT NULL,
            "secret_id" VARCHAR NOT NULL UNIQUE)''',
         'DROP TABLE "accounts"',
         ignore_errors='apply')
]
