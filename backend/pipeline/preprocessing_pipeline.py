from symspellpy import SymSpell, Verbosity
import pandas as pd
import regex
import string
import spacy
from pathlib import Path
# from sentence_transformers import SentenceTransformer
ASSET_DIR = Path(__file__).parent.parent / "assets"

# Symspell init
sym_spell = SymSpell(max_dictionary_edit_distance=1, prefix_length=7)
dict_path = ASSET_DIR / "frequency_dictionary_en_82_765.txt"
if not dict_path.exists():
    import symspellpy
    dict_path = Path(symspellpy.__file__).parent / "frequency_dictionary_en_82_765.txt"
sym_spell.load_dictionary(str(dict_path), 0, 1)

# Regex compilation
EMOJI_PATTERN = regex.compile(r'\p{Emoji}(?<!\d)')
UNIT_COMPOUND_PATTERN = regex.compile(r'^(\d+)([a-z]+)$')

# Allowed chars for spcl_chr_remover
allowed_chars = set(string.ascii_letters + string.digits)

# Allowed words and phrases
# Define protected vocabulary
PROTECTED_WORDS = {
    "dev", "prod", "staging", "repo", "api", "sdk", "ui", "ux",
    "frontend", "backend", "fullstack",
    "http", "https", "ftp", "ssh", "tcp", "ip","c","c++","c#"
    "json", "xml", "csv", "html", "css", "js", "ts",
    "cpu", "gpu", "ram", "ssd", "hdd",
    "vm", "os", "cli", "gui",
    "aws", "cpu", "gpu", "tpu", "nano", "coursera",
    "ai","h264","ml","mp4",
    "git","github","repository","tablet","tab","ai","bot"
}

KNOWN_UNITS = {
    "kb", "mb", "gb", "tb", "pb",
    "mhz", "ghz", "khz", "hz",
    "kbps", "mbps", "gbps",
    "px", "pt", "em", "rem",
    "ms", "ns", "us",
    "km", "cm", "mm", "nm",
    "mp"
}
ALLOWED_PUNCT = set(["+", ".", "_", "#"])

# Precompiled translation tables for optimized string processing
PUNCT_DELETION_CHARS = "".join(c for c in string.punctuation if c not in ALLOWED_PUNCT)
PUNCT_TRANSLATION_TABLE = str.maketrans("", "", PUNCT_DELETION_CHARS)
SPECIAL_CHAR_COUNT_TRANSLATOR = str.maketrans("", "", string.ascii_letters + string.digits)

# Pipeline starts here

# String validation
def validation(sentence):
    return sentence if isinstance(sentence, str) else ""

# Lowercase whole sentence
def lowercase(sentence):
    return sentence.lower() if isinstance(sentence, str) else ""

# Removes emojis from sentence using regex
def emoji_filter(sentence):
    return EMOJI_PATTERN.sub('', sentence) if isinstance(sentence, str) else ""

def remove_punctuation(sentence):
    if not isinstance(sentence, str):
        return ""
    return sentence.translate(PUNCT_TRANSLATION_TABLE)
# heyyy -> hey
def normalize_word(word, max_repeat=2):
    if not word:
        return word
    result = [word[0]]
    count = 1
    for i in range(1, len(word)):
        if word[i] == word[i-1]:
            count += 1
            if count <= max_repeat:
                result.append(word[i])
        else:
            count = 1
            result.append(word[i])
    return "".join(result)        

def repeat_character_filter(sentence):
    if not isinstance(sentence, str):
        return ""
    return " ".join(normalize_word(word) for word in sentence.split())

# Detects words with 
def filter_valid_tokens(sentence):
    if not isinstance(sentence, str):
        return ""
    valid_words = []
    for word in sentence.split():
        w = word.lower()
        if not w:
            continue
        # Pure numbers
        if w.isdigit():
            valid_words.append(word)
            continue
        # Number+unit compounds like 64kb, 30mhz
        if regex.match(r'^\d+[a-z]+$', w):
            unit_part = regex.sub(r'^\d+', '', w)
            if unit_part in KNOWN_UNITS:
                valid_words.append(word)
            continue
        if w in {"is", "to", "on", "in", "at", "by"}:
            valid_words.append(word)
            continue
        if len(set(w)) == 1:
            continue
        if len(w) <= 2 and not any(c in "aeiou" for c in w):
            continue
        valid_words.append(word)
    return " ".join(valid_words)


# Corrects spelling using symspellpy
def correct_spelling(sentence):
    if not isinstance(sentence, str):
        return ""
    corrected_words = []
    for word in sentence.split():
        w = word.lower()

        if w in PROTECTED_WORDS:
            corrected_words.append(word)
            continue

        if w.isdigit():
            corrected_words.append(word)
            continue

        compound_match = UNIT_COMPOUND_PATTERN.match(w)
        if compound_match:
            number_part = compound_match.group(1)
            unit_part = compound_match.group(2)
            if unit_part in PROTECTED_WORDS:
                corrected_words.append(word)
            else:
                suggestions = sym_spell.lookup(unit_part, Verbosity.CLOSEST, max_edit_distance=1)
                corrected_unit = suggestions[0].term if suggestions else unit_part
                corrected_words.append(number_part + corrected_unit)
            continue

        if len(w) <= 2:
            corrected_words.append(word)
            continue

        cleaned = regex.sub(r'[^a-zA-Z]', '', w)
        if not cleaned:
            corrected_words.append(word)
            continue

        suggestions = sym_spell.lookup(cleaned, Verbosity.CLOSEST, max_edit_distance=1)
        corrected_words.append(suggestions[0].term if suggestions else word)

    return " ".join(corrected_words)

# removes word if contains too many special characters
def special_character_remover(sentence):
    if not isinstance(sentence, str):
        return ""
    cleaned_words = []
    for word in sentence.split():
        if not word:
            continue
        # Use translate to remove alphanumeric characters, leaving only special characters
        special_count = len(word.translate(SPECIAL_CHAR_COUNT_TRANSLATOR))
        ratio = special_count / len(word)
        if ratio >= 0.3 and special_count > 3:
            continue
        cleaned_words.append(word)
    return " ".join(cleaned_words)

def unique_words(sentence):
    if not isinstance(sentence, str):
        return ""
    seen = set()
    result = []

    for word in sentence.split():
        if word not in seen:
            seen.add(word)
            result.append(word)

    return " ".join(result)

"""Proposed pipeline sequence : String validation -> lowercase -> emoji_filter -> normalize -> is_valid_token -> correct_spelling -> special_character_removal"""

def cleaning_pipeline(sentence):
    steps = [
        validation,
        lowercase,
        emoji_filter,
        remove_punctuation,
        repeat_character_filter,
        filter_valid_tokens,
        correct_spelling,
        special_character_remover,
        unique_words
    ]
    for step in steps:
        sentence = step(sentence)
    return sentence