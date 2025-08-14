# -*- coding: utf-8 -*-
import json
from langchain_community.llms import GigaChat
import re
import os

GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")


def get_cases_data():
    """Возвращает список кейсов с коротким контекстом."""
    with open("./data/eora_cases3.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
    # Формат: {"id": 1, "title": "...", "content": "...", "url": "..."}
    return cases


cases = get_cases_data()

try:
    llm = GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        verify_ssl_certs=False,
    )
except Exception as e:
    print(f"Ошибка инициализации GigaChat: {e}")
    llm = None


def select_relevant_topics(user_question: str, cases: list) -> list:
    """
    Возвращает список кейсов, релевантных вопросу пользователя.
    Используется первый запрос к LLM для фильтрации тем.
    """
    topics_list = "\n".join([f"[{i + 1}] {c['title']}" for i, c in enumerate(cases)])
    prompt = f"""
Вопрос пользователя: "{user_question}"

Из списка тем ниже выбери до 3 наиболее релевантных и верни только их номера через запятую:

{topics_list}
"""
    response = llm.invoke(prompt)
    numbers = [int(n.strip()) for n in response.split(",") if n.strip().isdigit()]
    # Возвращаем сами кейсы
    return [cases[n - 1] for n in numbers if 0 < n <= len(cases)]


def generate_answer(user_question: str, relevant_cases: list) -> str:
    """
    Формирует ответ LLM по выбранным кейсам.
    """
    context_parts = []
    for i, case in enumerate(relevant_cases, start=1):
        context_parts.append(
            f"[{i}] {case['title']}: {case['content']} (URL: {case['url']})"
        )
    context = "\n".join(context_parts)

    prompt = f"""
        Ты — умный и вежливый ассистент компании EORA.
        Отвечай кратко и только на основе предоставленного контекста.  
        Если используешь информацию из контекста, вставляй ссылки на источники в формате [номер источника].  

        КОНТЕКСТ:
        {context}

        ВОПРОС:
        {user_question}

        ОТВЕТ:
"""
    return llm.invoke(prompt)


def make_links_clickable(llm_response: str, relevant_cases: list) -> str:
    """
    Преобразует текст с [1], [2] в HTML ссылки для Telegram и Markdown жирный текст в <b>.
    """

    clickable_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", llm_response)
    url_map = {str(i + 1): case["url"] for i, case in enumerate(relevant_cases)}

    def repl(match):
        num = match.group(1)
        if num in url_map:
            return f'<a href="{url_map[num]}">[{num}]</a>'
        return match.group(0)

    clickable_text = re.sub(r"\[(\d+)\]", repl, clickable_text)

    return clickable_text


def get_eora_answer(user_question: str) -> str:
    relevant = select_relevant_topics(user_question, cases)
    if not relevant:
        return "К сожалению, по вашему вопросу не найдено подходящих кейсов."
    return make_links_clickable(generate_answer(user_question, relevant), relevant)
