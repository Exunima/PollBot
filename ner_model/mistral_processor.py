import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

# Путь к модели
model_path = "F:/BOT_TELEGRAM/PollBot/Mistral-7B"

# Настройка 4-bit квантования
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16"
)

# Загружаем токенизатор и модель
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
).to(device)

# Создаём пайплайн генерации текста
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

print("✅ Mistral-7B загружена успешно!")

# Дополняем/усиливаем шаблон, чтобы модель
# обязательно включала ключ "type":
prompt_template = """
Ты работаешь с текстами тестов и опросов.  
Твоя задача — **преобразовать PDF-тест в JSON строго в указанном формате** без номеров вопросов и буквенных маркеров, 
и обязательно указать ключ `"type"` = `"test"` или `"survey"`.  

---

### **📌 Определение типа:**
- Если в тексте есть **правильные ответы** (например, `"Ответ: A"`), это **ТЕСТ**.
- Если правильных ответов нет, это **ОПРОС**.

---

### **📌 Основные правила обработки:**
#### **1️⃣ Вопросы**
✅ Сохраняй **порядок следования** (игнорируя исходную нумерацию: римские/арабские цифры, символы).  
✅ Объединяй **разорванные вопросы** (например, начало на стр. 1, продолжение на стр. 2).  
✅ Удаляй **служебные пометки**: `[Вопрос №III]`, `(Раздел A)` и т.п.

#### **2️⃣ Варианты ответов**
✅ **Удаляй любые маркеры** (`а)`, `б)`, `1.`, `-` и т.д.) из текста варианта.  
✅ **Конвертируй маркеры** (`①`, `§`, `1.`, `б)`) в **плоский массив**.  
✅ **Сохраняй оригинальный порядок** вариантов.  

📌 **Пример преобразования:**  
**Исходник:** `§) int хранит целые числа...`  
**Результат:** `{ "text": "int хранит целые числа...", "correct": false }`  

---

### **📌 Определение правильных ответов в тестах**
✅ Если ответы указаны отдельно (например, `"1: в, 2: а,б"`), следуй этим правилам:
  1️⃣ **Сопоставляй номера вопросов** с их порядком появления.  
  2️⃣ **Конвертируй буквенные ответы в индексы массива вариантов**:  
     - `"в"` → 3-й вариант (`index = 2`)  
     - `"а,б"` → 1-й и 2-й варианты (`index = 0, 1`)  
✅ Если вопрос содержит **фразу `"несколько ответов"`**, **отмечай несколько `correct: true`**.

---

### **📌 Формат вывода (ТОЛЬКО JSON, без пояснений и текста!):**
```json
{
  "type": "test" или "survey",
  "title": "Тема из PDF",
  "questions": [
    {
      "text": "Полный текст вопроса...",
      "options": [
        { "text": "вариант 1", "correct": false },
        { "text": "вариант 2", "correct": true }
      ]
    },
    ...
  ]
}


📌 **Текст для обработки:**
{text}
"""


def extract_json(text):
    """Извлекает JSON-объект из сгенерированного текста"""
    text = text.strip()
    # Удаляем возможные блоки Markdown ```json ... ```
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Ищем блок, начинающийся с { и заканчивающийся }
    match = re.search(r"{.*?}", text, re.DOTALL)
    if match:
        json_text = match.group(0).strip()
        return json_text
    return None


def clean_json_keys(json_data):
    """Рекурсивно удаляет лишние пробелы из ключей JSON"""
    if isinstance(json_data, dict):
        return {k.strip(): clean_json_keys(v) for k, v in json_data.items()}
    elif isinstance(json_data, list):
        return [clean_json_keys(item) for item in json_data]
    return json_data


def guess_type_by_text(raw_text: str) -> str:
    """
    Простейшая эвристика:
    Если видим "Ответ:" или "Answer:" в сыром тексте → считаем, что это тест,
    иначе → опрос.
    """
    lower_text = raw_text.lower()
    if "ответ:" in lower_text or "answer:" in lower_text:
        return "test"
    return "survey"


def process_text_with_mistral(text: str):
    """Обрабатывает текст и возвращает JSON с тестами/опросами, гарантируя, что есть ключ 'type'."""

    # Заменяем фигурные скобки, чтобы избежать KeyError в .format()
    safe_text = text.replace("{", "{{").replace("}", "}}")
    prompt = prompt_template.replace("{text}", safe_text)

    result = generator(
        prompt,
        max_new_tokens=700,
        temperature=0.1,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=False
    )[0]["generated_text"]

    print("🔍 Ответ модели (сырые данные):\n", result)

    extracted_json = extract_json(result)
    if not extracted_json:
        ...
        return {
            "type": guess_type_by_text(text),
            "title": "Без названия",
            "questions": []
        }

    try:
        structured_data = json.loads(extracted_json)
        if isinstance(structured_data, list) and len(structured_data) > 0:
            structured_data = structured_data[0]
    except json.JSONDecodeError as e:
        ...
        return {
            "type": guess_type_by_text(text),
            "title": "Без названия",
            "questions": []
        }

    # Приводим ключи в порядок
    structured_data = clean_json_keys(structured_data)

    # Если нет "type", добавляем
    if "type" not in structured_data:
        print("❌ Ошибка: В JSON отсутствует ключ 'type'. Добавляем принудительно.")
        structured_data["type"] = guess_type_by_text(text)

    # [НОВОЕ] Если нет "title", подставляем "Без названия"
    if "title" not in structured_data:
        print("❌ Ошибка: В JSON отсутствует ключ 'title'. Добавляем принудительно.")
        structured_data["title"] = "Без названия"

    # [НОВОЕ] Если нет "questions", добавляем пустой список
    if "questions" not in structured_data:
        print("❌ Ошибка: В JSON отсутствует ключ 'questions'. Добавляем пустой список принудительно.")
        structured_data["questions"] = []

    print("✅ Полученный JSON:", json.dumps(structured_data, indent=2, ensure_ascii=False))
    return structured_data

