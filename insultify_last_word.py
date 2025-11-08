import re

VOWELS = "аеёиоуыэюя"
MAP = {
    "а": "хуя", "я": "хуя",
    "э": "хуе", "е": "хуе",
    "ы": "хуи", "и": "хуи",
    "о": "хуё", "ё": "хуё",
    "у": "хую", "ю": "хую",
}

def _match_case(prefix: str, word: str) -> str:
    if word.isupper():
        return prefix.upper()
    if word[:1].isupper():
        return prefix.capitalize()
    return prefix

def insultify_word(word: str, use_yo: bool = True) -> str:
    idx = None
    for i, ch in enumerate(word):
        lo = ch.lower()
        if lo in VOWELS:
            idx = i
            v = lo
            break
    if idx is None:
        return word

    prefix = MAP[v]
    if not use_yo and v in ("о", "ё"):
        prefix = "хуе"

    prefix = _match_case(prefix, word)
    rest = word[idx+1:]
    return prefix + rest

WORD_RE = re.compile(r"[А-Яа-яЁё]+")

def insultify_last_word(text: str, use_yo: bool = True) -> str:
    last_match = None
    for m in WORD_RE.finditer(text):
        last_match = m
    if not last_match:
        return text
    w = last_match.group(0)
    new_w = insultify_word(w, use_yo=use_yo)
    return new_w + text[last_match.end():]

