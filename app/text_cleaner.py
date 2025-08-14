import json
import re


def clean_text_for_embedding(text: str) -> str:
    """
    Приводит текст из парсинга сайта к нормальному виду для эмбеддингов:
    - убирает навигацию и декоративные разделители (/ , 01/ и т.п.)
    - убирает лишние переносы строк и пустые строки
    - схлопывает повторяющиеся пробелы
    - оставляет только осмысленный текст
    """
    text = re.sub(
        r"^[\w\sА-Яа-яёЁ]+(\s*/\s*[\w\sА-Яа-яёЁ]+)+$", "", text, flags=re.MULTILINE
    )
    text = re.sub(r"\b\d{1,2}\s*/\s*\b", "", text)
    text = re.sub(r"\n\s*/\s*\n", "\n", text)
    text = re.sub(r"^[A-Za-zА-Яа-яёЁ]{2,3}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()
    return text


def normalize_case_text(content: str) -> str:
    """
    Нормализует длинный текст кейса для эмбеддингов:
    - убирает лишние переносы строк внутри предложений
    - удаляет неразрывные пробелы
    - убирает повторяющиеся заголовки
    - удаляет явно служебные/юридические фразы
    - схлопывает лишние пробелы
    """
    text = content.replace("\xa0", " ")
    lines = text.split("\n")
    cleaned_lines = []
    prev = None
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped != prev:
            cleaned_lines.append(line_stripped)
        prev = line_stripped
    text = "\n".join(cleaned_lines)

    text = re.sub(r"Нажимая на.*Политик[^\n]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()

    return text


with open("./data/eora_cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

results = []

for case in cases:
    case["content"] = normalize_case_text(case["content"])
    results.append(case)

for case in results:
    print(case)
    print()
with open("./data/eora_cases.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
