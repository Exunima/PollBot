# PollBot — Telegram-бот для создания и прохождения опросов и тестов

**PollBot** — это интеллектуальный Telegram-бот, который позволяет автоматически создавать и проходить опросы и тесты.

## Возможности

- 📄 Загрузка PDF и изображений  
- 🔍 Распознавание текста (Tesseract OCR)  
- 🧠 Интеграция с Mistral-7B для анализа структуры тестов и опросов  
- ✍️ Ручной режим создания вопросов  
- 🔑 Генерация уникального ключа доступа  
- ⏱️ Ограничения по времени и числу попыток  
- 📊 Сбор статистики по ответам  
- 🗑️ Автоматическое удаление по истечении срока действия  

---

## Стек технологий

- **Python 3.10+**  
- **Aiogram v3** — асинхронный Telegram-фреймворк  
- **SQLite + Tortoise ORM**  
- **Tesseract OCR**  
- **Transformers + Mistral-7B**  
- **Развёртывание**: VPS / PythonAnywhere  

---

## 🛠️ Как запустить

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Установите Tesseract OCR:

[Скачать Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

3. Создайте файл .env:

```env
BOT_TOKEN=<ваш_токен_от_BotFather>
TESSERACT_PATH="C:/Program Files/Tesseract-OCR/tesseract.exe"
```

4. Инициализируйте базу данных:

```bash
python database/db_init.py
```

5. Запустите бота:

```bash
python main.py
```

---

## Пример структуры JSON

```json
{
  "title": "Мой тест",
  "questions": [
    {
      "text": "Сколько будет 2+2?",
      "options": [
        { "text": "3", "correct": false },
        { "text": "4", "correct": true }
      ]
    }
  ]
}
```

---

## Как это работает

1. Пользователь загружает PDF/фото или создаёт тест вручную

2. OCR извлекает текст (если фото)

3. Текст анализируется моделью Mistral-7B

4. Данные сохраняются в SQLite

5. Бот отправляет пользователю ключ доступа

6. Участники вводят ключ и проходят опрос/тест

---

## Автор
- Telegram: [@Exunima](https://t.me/Exunima)
- GitHub: [Exunima](https://github.com/Exunima)
