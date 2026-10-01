"""Переносит слова и стихи из таблиц в расширение: python -m gospel_oracle.build_extension

Расширение браузера не умеет читать наши csv-таблицы, поэтому питон
перекладывает их в файл extension/data.js, который расширение уже понимает.
Запускай эту команду каждый раз после того, как поменяла words.csv или verses.csv.
"""

import json
from pathlib import Path

from .gospel import VERSES, WORDS

target = Path(__file__).parent.parent / "extension" / "data.js"

target.write_text(
    "// Этот файл создаёт питон: python -m gospel_oracle.build_extension\n"
    "// Не меняй его руками, меняй таблицы words.csv и verses.csv.\n\n"
    f"const WORDS = {json.dumps(WORDS, ensure_ascii=False, indent=2)};\n\n"
    f"const VERSES = {json.dumps(VERSES, ensure_ascii=False, indent=2)};\n",
    encoding="utf-8",
)

print("Готово: слова и стихи перенесены в", target)
