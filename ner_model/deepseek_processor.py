import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

deepseek_prompt = """
Ты работаешь с текстами тестов и опросов.
Твоя задача — структурировать их для базы данных.

⚠️ Внимание: тест и опрос - это РАЗНЫЕ вещи! Не путай их!
📌 Если в тексте есть правильные ответы - это ТЕСТ.
📌 Если правильных ответов нет - это ОПРОС.

🔹 **Формат для ОПРОСА:**
{
  "type": "survey",
  "title": "Название опроса",
  "questions": [
    {
      "text": "Текст вопроса",
      "options": ["Ответ 1", "Ответ 2", "Ответ 3"]
    }
  ]
}

🔹 **Формат для ТЕСТА:**
{
  "type": "test",
  "title": "Название теста",
  "questions": [
    {
      "text": "Текст вопроса",
      "options": [
        {"text": "Ответ 1", "correct": False},
        {"text": "Ответ 2", "correct": True}
      ]
    }
  ]
}

Верни ТОЛЬКО JSON, без пояснений! Если не можешь, верни `{"error": "Ошибка"}`.

Текст для обработки:
{input_text}
"""

model_path = "F:/BOT_TELEGRAM/PollBot/deepseek_models"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

cached_model = None
cached_tokenizer = None
cached_generator = None


def load_deepseek_model():
    global cached_model, cached_tokenizer, cached_generator

    if cached_model is None:
        print("🔄 Загружаем DeepSeek в память...")
        cached_model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True
        ).to(device)
        cached_tokenizer = AutoTokenizer.from_pretrained(model_path)
        cached_generator = pipeline(
            "text-generation",
            model=cached_model,
            tokenizer=cached_tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        print("✅ Модель DeepSeek загружена в память!")

    return cached_generator


def process_text_with_deepseek(text):
    generator = load_deepseek_model()

    prompt = deepseek_prompt.format(input_text=text)

    result = generator(
        prompt,
        max_new_tokens=500,
        temperature=0.5,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )[0]["generated_text"]

    print("🔍 Ответ модели:\n", result)  # Вывод в консоль

    # Проверяем, является ли результат корректным JSON
    try:
        parsed_json = json.loads(result.strip())

        # Проверяем, есть ли ключ "type"
        if "type" not in parsed_json:
            print("❌ Ошибка: JSON не содержит 'type'.")
            return None

        return parsed_json
    except json.JSONDecodeError:
        print("❌ Ошибка: DeepSeek вернул некорректный JSON.")
        return None  # Вернём None, чтобы бот не упал
