"""Питон-оракул: находит семь смертных грехов в тексте и отвечает стихом из Евангелия."""

import csv
import random
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Папка с таблицами лежит рядом с этим файлом
DATA = Path(__file__).parent / "data"


# ---------- 1. Загружаем датасет из таблиц ----------

def load_table(filename):
    """Читает csv-таблицу. Каждая строка становится словарём {название столбца: значение}."""
    with open(DATA / filename, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# WORDS = {"Алчность": ["купи", "скидк", ...], "Лень": [...], ...}
WORDS = {}
for row in load_table("words.csv"):
    sin = row["грех"]
    if sin not in WORDS:
        WORDS[sin] = []
    WORDS[sin].append(row["начало слова"])

# VERSES = {"Алчность": ["«Не можете служить Богу и маммоне» (Мф 6:24)", ...], ...}
VERSES = {}
for row in load_table("verses.csv"):
    sin = row["грех"]
    if sin not in VERSES:
        VERSES[sin] = []
    VERSES[sin].append(f"«{row['текст']}» ({row['ссылка']})")


# ---------- 2. Ищем грехи в тексте ----------

def count_sins(text):
    """Считает, сколько раз в тексте встречается каждый грех.

    Слово «скидки» начинается с «скидк» из таблицы, значит это алчность.
    Возвращает словарь, например {"Алчность": 5, "Гнев": 2}.
    """
    counts = {}
    for word in re.findall(r"\w+", text.lower()):  # все слова текста по очереди
        for sin, stems in WORDS.items():
            if word.startswith(tuple(stems)):
                counts[sin] = counts.get(sin, 0) + 1
    return counts


def main_sin(text):
    """Главный грех текста: тот, что встретился чаще всего. Если грехов нет, то None."""
    if text.capitalize() in WORDS:  # человек сразу написал название греха
        return text.capitalize()
    counts = count_sins(text)
    if not counts:
        return None
    return max(counts, key=counts.get)


# ---------- 3. Класс Gospel: print выдаёт стих ----------

class Gospel:
    """print(Gospel("лень")) печатает стих про лень.

    Gospel()                — случайный стих
    Gospel("гнев")          — стих про гнев
    Gospel("хочу бургер")   — грех угадывается по словам
    """

    def __init__(self, text=""):
        self.sin = main_sin(text)

    def __repr__(self):
        # Этот метод питон вызывает сам, когда объект печатают через print
        if self.sin is None:
            all_verses = [verse for verses in VERSES.values() for verse in verses]
            return random.choice(all_verses)
        return random.choice(VERSES[self.sin])


# ---------- 4. Проверка сайта: команда gospel <ссылка> ----------

def download_text(url):
    """Скачивает страницу и оставляет только текст, который видит человек."""
    if not url.startswith("http"):
        url = "https://" + url
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()  # если сайт ответил ошибкой, дальше не идём
    soup = BeautifulSoup(response.content, "html.parser")
    for tag in soup(["script", "style"]):  # код и оформление страницы — не текст
        tag.decompose()
    return soup.get_text(" ")


def print_report(counts):
    """Печатает отчёт: сколько каких грехов и стих под главный из них."""
    total = sum(counts.values())
    print("Грехов на странице:", total)
    if total == 0:
        print("✝", random.choice(VERSES["Чистая страница"]))
        return

    biggest = max(counts.values())
    for sin in sorted(counts, key=counts.get, reverse=True):
        bar = "█" * max(1, counts[sin] * 24 // biggest)
        print(f"{sin:<12} {bar} {counts[sin]}")

    top = max(counts, key=counts.get)
    print("✝", random.choice(VERSES[top]))


def main():
    """Запускается командой в терминале: gospel https://lenta.ru"""
    if len(sys.argv) < 2:
        print("Напиши ссылку, например: gospel https://lenta.ru")
        return
    try:
        text = download_text(sys.argv[1])
    except requests.RequestException:
        print("Не удалось открыть страницу. Проверь ссылку или попробуй другой сайт.")
        return
    print_report(count_sins(text))
