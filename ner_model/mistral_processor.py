import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Загружаем модель Mistral-7B
model_name = "mistralai/Mistral-7B-Instruct-v0.2"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto").to(device)

# Создаём пайплайн генерации
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)


def process_text_with_mistral(text):
    """Обрабатывает текст и возвращает структурированные данные"""
    prompt = f"""
    Ты работаешь с текстами тестов и опросов.
    Твоя задача — структурировать их для базы данных.

    ⚠️ Внимание: тест и опрос - это РАЗНЫЕ вещи! Не путай их!
    📌 Если в тексте есть правильные ответы - это ТЕСТ.
    📌 Если правильных ответов нет - это ОПРОС.

    🔹 **Формат для ОПРОСА:**
    {{
      "type": "survey",
      "title": "Название опроса",
      "questions": [
        {{
          "text": "Текст вопроса",
          "options": ["Ответ 1", "Ответ 2", "Ответ 3"]
        }}
      ]
    }}

    🔹 **Формат для ТЕСТА:**
    {{
      "type": "test",
      "title": "Название теста",
      "questions": [
        {{
          "text": "Текст вопроса",
          "options": [
            {{"text": "Ответ 1", "correct": False}},
            {{"text": "Ответ 2", "correct": True}}
          ]
        }}
      ]
    }}

    🔴 ВАЖНО: Верни ТОЛЬКО JSON-объект, без пояснений, комментариев и лишнего текста.  
    Если не можешь определить тип, верни `{{"error": "Не удалось определить тип"}}`.

    Текст для обработки:
    {text}
    """

    result = generator(
        prompt,
        max_new_tokens=500,
        temperature=0.5,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )[0]["generated_text"]

    print("🔍 Ответ модели (сырые данные):\n", result)  # Вывод в консоль
    return result
