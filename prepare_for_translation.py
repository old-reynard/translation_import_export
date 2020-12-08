import os
import json
import csv
from datetime import datetime
from typing import List

from utils import die

# home directory for the project
home = os.environ.get('HVR_HOME')
if not home:
    die('Home directory not found')

# directory with all string resources in it
resource_folder = f'{home}/lib/l10n'
# source file with raw string resources
# this is where the app exports all translatable resources to
source = f'{resource_folder}/intl_messages.arb'


def meaningful_key(k: str) -> bool:
    return not k.startswith('@')


def is_language_file(name: str) -> bool:
    return name.startswith('intl_') and ('messages' not in name)


def find_language_files(directory: str) -> List[os.DirEntry]:
    return [file for file in os.scandir(directory) if is_language_file(file.name)]


def parse(files: List[os.DirEntry]) -> dict:
    return {get_locale_name(file.name): json.loads(open(file).read()) for file in files}


# intl_en_CA.arb
def get_locale_name(filename: str) -> str:
    return filename.rstrip('.arb').lstrip('intl_')


resources = open(source)
source_files = find_language_files(resource_folder)
languages = parse(source_files)

main_arb_file = resources.read()
main_parsed: dict = json.loads(main_arb_file)

keys = list(filter(meaningful_key, main_parsed.keys()))

data = []

for key in keys:
    secondary_key = f'@{key}'
    locales = {
        'source': main_parsed.get(key),
        'desc': main_parsed.get(secondary_key).get('description'),
        'type': main_parsed.get(secondary_key).get('type'),
        'placeholders': main_parsed.get(secondary_key).get('placeholders'),
        **languages,
    }
    data.append({key: locales})

now = datetime.now()
date = f'{now.year}-{now.month}-{now.day}'
output = open(f'source/source_for_translation_{date}.csv', mode='w')
writer = csv.writer(output)

writer.writerow(['id', 'source', 'description'] + list(languages.keys()) + ['type', 'placeholders'])

for line in data:
    key = list(line.keys())[0]
    value = line[key]
    source = value.get('source', '')
    desc = value.get('desc', '')
    t = value.get('type', '')
    placeholders = value.get('placeholders', '')
    row = [key, source, desc]
    for resource in languages.values():
        row.append(resource.get(key))
    row.append(t)
    row.append(placeholders)
    writer.writerow(row)
