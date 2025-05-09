import re

def category_values_order(s: str):
    words = set(s.split())
    ORDERED_WORDS = {
        1: {"я", "меня", "мне", "мной", "мой", "один", "одна", "одно", "одни"},
        2: {"ты", "тебя", "тебе", "тобой", "твой", "два", "две", "двое"},
        3: {"(справа)", "три", "трое"},
        4: {"(слева)", "четыре", "четверо"},
        5: {"пять", "пятеро"},
        6: {"шесть", "шестеро"},
        7: {"семь", "семеро"},
        8: {"восемь"},
        9: {"девять"},
        10: {"десять"}
    }
    for i, wordlist in ORDERED_WORDS.items():
        if words & wordlist: return i
    return i + 1

def url_root(s: str):
    return re.sub(r"https?://|/.+", "", s)