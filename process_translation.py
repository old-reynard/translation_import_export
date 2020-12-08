import csv
import json
import re
from typing import List

translations_path = 'source/source_for_translation_2020-11-25.csv'
locale_regex = r'([a-z]{2})_([A-Za-z]{2})'


class Translation:
    def __init__(self, l_name: str = None, resources: dict = None):
        self.locale = l_name
        self.resources = resources

    def __str__(self):
        return f'{self.locale}: {self.resources}'

    def __repr__(self):
        return str(self)


def is_locale(header: str):
    return re.search(locale_regex, header) is not None


def parse(path: str) -> List[dict]:
    file = open(path)
    lines = csv.DictReader(file)
    return list(lines)


parsed = parse(translations_path)
if not parsed:
    print('No resources')
    exit()

locale_names = list(filter(is_locale, parsed[0].keys()))
translations = {name: Translation(l_name=name, resources={}) for name in locale_names}
for d in parse(translations_path):
    key = d.get('id')
    desc = d.get('description')
    t = d.get('type')
    placeholders = d.get('placeholders')
    locales = [{key: value} for key, value in d.items() if is_locale(key)]
    for locale in locales:
        for locale_name, translation in locale.items():
            relevant_translation: Translation = translations.get(list(locale.keys())[0])
            relevant_translation.resources[key] = translation
            relevant_translation.resources[f'@{key}'] = {
                'description': desc,
                'type': t,
                'placeholders': placeholders,
            }

for name, translation in translations.items():
    lang, country_code = name.split('_')
    formatted = f'{lang}_{country_code.upper()}'
    translation.resources['@@locale'] = formatted
    arb = open(f'intl_{formatted}.arb', mode='w', encoding='utf-8')
    json.dump(translation.resources, arb, indent=4, ensure_ascii=False)
