"""Проверка стихов: python -m gospel_oracle.check

Каждый стих из verses.csv ищется в настоящем Синодальном переводе (data/gospels.json).
Если хоть одно слово не совпадает, проверка это покажет.
"""

import json
import re

from .gospel import DATA, load_table


def only_words(text):
    """Оставляет только слова: без регистра, букв ё, ударений и знаков препинания."""
    text = text.lower().replace("ё", "е").replace("́", "")  # ́ — знак ударения
    return " ".join(re.findall(r"\w+", text))


gospels = json.loads((DATA / "gospels.json").read_text(encoding="utf-8"))
errors = 0

for row in load_table("verses.csv"):
    book, place = row["ссылка"].split()          # "Мф 6:24" → "Мф", "6:24"
    chapter, verse = place.split(":")            # "6:24"    → "6", "24"
    original = gospels[book][int(chapter) - 1][int(verse) - 1]

    if only_words(row["текст"]) in only_words(original):
        print("✓", row["ссылка"])
    else:
        errors += 1
        print("✗", row["ссылка"], "— не совпадает")
        print("   в таблице: ", row["текст"])
        print("   в переводе:", original)

print()
print("Ошибок:", errors)
