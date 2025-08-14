# EORA AI Assistant Bot 🤖


**EORA AI Assistant** — это Telegram-бот, который отвечает на вопросы пользователей, используя контекстные кейсы компании EORA.

---

## 📦 Технологии
- Python 3.13  
- [Aiogram 3](https://docs.aiogram.dev/en/latest/) — фреймворк для Telegram-бота  
- [GigaChat API](https://gigachat.example.com) — языковая модель для генерации ответов  
- [LangChain](https://www.langchain.com/) — для реализации RAG цепочки  
- Docker & Docker Compose — для контейнеризации проекта  
- ChromaDB — для векторного поиска кейсов  

---

## 🚀 Установка и запуск

### 1. Клонируем репозиторий
```bash
git clone https://github.com/StarLightAmogus/EoraAIAgent.git
cd EoraAIAgent
```
### 2. Настройка переменных окружения
Создайте файл .env в корне проекта и добавьте токены:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
GIGACHAT_CREDENTIALS=ваш_токен_gigachat
```
### 3. Запуск локально (без Docker)
Создайте виртуальное окружение и установите зависимости:
```python
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```
### 4. Запуск с Docker
```
docker compose up --build
```
## Протестируйте бота здесь - [@EoraAI_bot](https://t.me/EoraAI_bot)

## 🔍 Модуль поиска информации

- `search_module.py` — реализует поиск кейсов с помощью **эмбеддингов**. Подходит для экспериментов и небольших наборов данных.  
- `search_module2.py` — основной модуль, который используется в проекте для работы с ботом.  
  Он применяет **двойное обращение к GigaChat**: сначала для определения релевантных тем по вопросу пользователя, а затем для генерации ответа на основе выбранного контекста.  
  Такой подход позволяет создавать более точные и информативные ответы.
