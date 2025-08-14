import requests
from bs4 import BeautifulSoup
import time
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
}


def fetch_with_retries(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"Ошибка {e}, попытка {attempt + 1} из {retries}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def clean_text_for_embedding(text: str) -> str:
    """
    Приводит текст из парсинга сайта к нормальному виду для эмбеддингов:
    - убирает навигацию и декоративные разделители (/ , 01/ и т.п.)
    - убирает лишние переносы строк и пустые строки
    - схлопывает повторяющиеся пробелы
    - оставляет только осмысленный текст
    """
    # 1. Убираем навигационные цепочки вида "Главная / Портфолио / ..."
    text = re.sub(
        r"^[\w\sА-Яа-яёЁ]+(\s*/\s*[\w\sА-Яа-яёЁ]+)+$", "", text, flags=re.MULTILINE
    )

    # 2. Убираем отдельные цифры и порядковые вроде "01/", "02/"
    text = re.sub(r"\b\d{1,2}\s*/\s*\b", "", text)

    # 3. Убираем декоративные слэши между \n
    text = re.sub(r"\n\s*/\s*\n", "\n", text)

    # 4. Убираем метки типа "En", "RU" в начале строк
    text = re.sub(r"^[A-Za-zА-Яа-яёЁ]{2,3}\s*$", "", text, flags=re.MULTILINE)

    # 5. Убираем лишние переносы строк (>2 подряд -> 1)
    text = re.sub(r"\n{2,}", "\n", text)

    # 6. Схлопываем повторяющиеся пробелы
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 7. Обрезаем пробелы по краям
    text = text.strip()

    return text


def parse_case(url):
    html = fetch_with_retries(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Заголовок
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    for form_block in soup.find_all(class_="t-form"):
        form_block.decompose()

    for nav_block in soup.find_all(["header", "nav", "footer"]):
        nav_block.decompose()

    content_containers = soup.find(["article", "main"])
    if not content_containers:
        content_containers = soup.find(
            class_=re.compile(r"content|main-content|article|post-body")
        )

    if not content_containers:
        content_containers = soup.body

    for tag in content_containers.find_all(["script", "style", "form", "aside"]):
        tag.decompose()

    text = content_containers.get_text(separator="\n\n", strip=True)

    text = re.sub(r"[\w.-]+@[\w.-]+|\+?\d[\d\s-]+\d", "", text)
    text = re.sub(r"\[\{.*\}\]", "", text)
    text = re.sub(r"Напишите нам|Отправить", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*\n", "\n\n", text).strip()
    text = clean_text_for_embedding(text)

    return {"url": url, "title": title, "content": text}


def main():
    with open("./data/EoraLinks.txt", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    results = []
    for url in urls:
        print(f"Парсим: {url}")
        data = parse_case(url)
        if data:
            results.append(data)

    with open("./data/eora_cases.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
