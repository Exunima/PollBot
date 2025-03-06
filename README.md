
# 🤖 Telegram Bot — PollBot

## Что это?
PollBot — это Telegram-бот для создания опросов и тестов.  
Он умеет:
- Создавать анонимные и обычные опросы.
- Делать тесты с правильными ответами.
- Работать с изображениями (распознавание текста через Tesseract).
- Ограничивать время прохождения опросов.
- Удалять старые опросы и тесты автоматически.

---

## Как запустить?

### Скачай проект
Клонируй репозиторий на свой компьютер:
```bash
git clone https://github.com/Exunima/PollBot.git
cd PollBot
```

### Установи зависимости
Если еще нет файла `requirements.txt`, создай его:
```bash
pip freeze > requirements.txt
```
Установи зависимости:
```bash
pip install -r requirements.txt
```

### Создай файл `.env` в папке с проектом
Пример содержимого `.env`:
```env
TOKEN=твой_токен_бота
TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Подготовь базу данных
Выполни команду:
```bash
python database/db_init.py
```

### Запусти Redis (если нужен)
Убедись, что Redis запущен локально на порту `6379`.

### Запусти бота
```bash
python main.py
```

Готово!

---

## Автор
- Telegram: [@Exunima](https://t.me/Exunima)
- GitHub: [Exunima](https://github.com/Exunima)
