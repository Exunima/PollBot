from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

deepseek_prompt = """
Ты работаешь с текстами тестов и опросов.
Твоя задача — выделить следующие элементы из текста:
- Название теста или опроса.
- Каждый вопрос.
- Варианты ответов для каждого вопроса.
- Правильный ответ (если указан).

Верни результат строго в формате JSON:
{
  "title": "Название теста",
  "questions": [
    {
      "question": "Текст вопроса",
      "options": ["Ответ 1", "Ответ 2", "Ответ 3"],
      "correct": "Правильный ответ"
    }
  ]
}

Текст для обработки:
{}
"""


def process_text_with_deepseek(text):
    model_path = "F:/BOT_TELEGRAM/PollBot/deepseek_models"

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto"
    )

    prompt = deepseek_prompt.format(text)

    result = generator(prompt, max_new_tokens=2000, do_sample=False)

    return result[0]["generated_text"]
