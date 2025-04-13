def category_values_order(s: str):
    words = set(s.split())
    ORDERED_WORDS = {
        1: {"я", "меня", "мне", "мной", "мой"},
        2: {"ты", "тебя", "тебе", "тобой", "твой"},
        3: {"(справа)"},
        4: {"(слева)"}
    }
    for i, wordlist in ORDERED_WORDS.items():
        if words & wordlist: return i
    return i + 1