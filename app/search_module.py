# -*- coding: utf-8 -*-

import json
from typing import List
from langchain.prompts import PromptTemplate 
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableMap, RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from langchain_community.llms import GigaChat 

#Загружаем обработанные данные
def get_cases_data():
    with open("./data/eora_cases3.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_documents_from_cases(cases):
    """Преобразует кейсы в формат документов для LangChain."""
    documents = []
    for case in cases:
        # заголовок и контент для полноты информации объединяется
        page_content = f"Заголовок: {case['title']}\nСодержание: {case['content']}"
        documents.append(
            {
                "page_content": page_content,
                "metadata": {"url": case["url"], "title": case["title"]},
            }
        )
    return documents


# СОЗДАНИЕ И ЗАГРУЗКА ВЕКТОРНОЙ БАЗЫ ДАННЫХ
embedding_function = SentenceTransformerEmbeddings(
    model_name="intfloat/multilingual-e5-large"
)

# Загружаем наши кейсы
documents = create_documents_from_cases(get_cases_data())

# Создаем векторную базу данных ChromaDB из наших документов.
# Она будет создана в папке 'chroma_db' и сохранена на диске.
vectorstore = Chroma.from_texts(
    texts=[doc["page_content"] for doc in documents],
    embedding=embedding_function,
    metadatas=[doc["metadata"] for doc in documents],
    persist_directory="./chroma_db",
)

# Создаем "ретривер" - специальный объект для поиска по базе данных
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)  # Искать 5 самых релевантных документа

print("✅ Векторная база данных успешно создана и готова к работе.")


# --- 3. НАСТРОЙКА ЯЗЫКОВОЙ МОДЕЛИ И RAG-ЦЕПОЧКИ ---
try:
    llm = GigaChat(
        credentials="YmMwMDE5ZjAtOTM0MS00MzUxLTk1NjAtODg2OGZiYTEzNjA5OjAyZWVlNDRiLWI5MDMtNGQxMC04MGY0LTUwZGQ0NmY4MjgyZA==",
        verify_ssl_certs=False,
    )
except Exception as e:
    print(
        f"Не удалось инициализировать GigaChat. Убедитесь, что токен указан верно. Ошибка: {e}"
    )
    llm = None 

# Создаем шаблон промпта. Это сердце RAG-системы.
# Он говорит модели, как себя вести и откуда брать информацию.
template = """
Ты — умный и вежливый ассистент компании EORA.  
Отвечай на вопросы пользователя, основываясь ИСКЛЮЧИТЕЛЬНО на предоставленном ниже контексте.  
Отвечай кратко и по делу. Не используй собственные знания, только то, что есть в контексте.  
Если в контексте нет ответа на вопрос — вежливо сообщи об этом.  

Требования к ответу:  
1. Если в ответе используется информация из контекста, обязательно вставляй ссылки на источники в формате [номер источника] сразу после соответствующего предложения или факта.  
2. Номера источников должны соответствовать порядку, в котором они указаны в контексте.  
3. После текста ответа обязательно добавь список источников строго в формате:  
Источники:  
[1] Название источника 1: URL-адрес 1  
[2] Название источника 2: URL-адрес 2  

Пример ответа:  
Компания разрабатывала бота для HR в «Магнит» [1], а также реализовала поиск по картинкам для KazanExpress [2].  

КОНТЕКСТ:  
{context}  

ВОПРОС:  
{question}  

ОТВЕТ:
"""

prompt = PromptTemplate.from_template(template)


def format_docs(docs: List):
    """Форматирует документы с нумерацией источников."""
    parts = []
    for i, doc in enumerate(docs, start=1):
        source = f"[Источник {i}]\nНазвание: {doc.metadata.get('title', 'N/A')}\nURL: {doc.metadata.get('url', 'N/A')}"
        parts.append(f"{doc.page_content}\n\n{source}")
    return "\n\n---\n\n".join(parts)


# Собираем все компоненты в единую цепочку (RAG chain)
if llm:
    chain_input = RunnableMap(
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
    )
    rag_chain = chain_input | prompt | llm | StrOutputParser()
else:
    raise RuntimeError("Ошибка объединения компонентов RAG")



def get_eora_answer(question):
    """Возвращает ответ ассистента на вопрос."""
    return rag_chain.invoke(question)
