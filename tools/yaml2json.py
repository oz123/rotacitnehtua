#!/usr/bin/env python3
"""
YAML database to JSON converter.
"""
import json
import tempfile
from collections import OrderedDict
from glob import glob
from os import path, remove
from shutil import rmtree
from subprocess import call
import sys
try:
    import yaml
except ImportError:
    sys.exit("Please install pyaml first")

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser



GIT_CLONE_URI = "https://github.com/2factorauth/twofactorauth"
TMP_FOLDER = path.join(tempfile.gettempdir(), "Authenticator")
DATA_DIR = path.join(TMP_FOLDER, "_data")
OUTPUT_DIR = path.join(path.dirname(
    path.realpath(__file__)), "../data/data.json")

print("Cloning the repository...")
if path.exists(TMP_FOLDER):
    rmtree(TMP_FOLDER)
call(["git", "clone", "--depth=1", GIT_CLONE_URI, TMP_FOLDER])

if path.exists(OUTPUT_DIR):
    remove(OUTPUT_DIR)


def is_valid(provider):
    if set(["tfa", "software"]).issubset(provider.keys()):
        return provider["tfa"] and provider["software"]
    else:
        return False


output = {}

html_parser = HTMLParser()

for db_file in glob(DATA_DIR + "/*.yml"):
    with open(db_file, 'r', encoding='utf8') as file_data:
        try:
            providers = yaml.load(file_data)["websites"]
            for provider in providers:
                if is_valid(provider):
                    name = provider.get("name")
                    output[html_parser.unescape(name)] = {
                        "img": provider.get("img"),
                        "url": provider.get("url", ""),
                        "doc": provider.get("doc", "")
                    }
        except (yaml.YAMLError, TypeError, KeyError) as error:
            pass
output = OrderedDict(sorted(output.items(), key=lambda x: x[0].lower()))

with open(OUTPUT_DIR, 'w') as data:
    json.dump(output, data, indent=4)

rmtree(TMP_FOLDER)
