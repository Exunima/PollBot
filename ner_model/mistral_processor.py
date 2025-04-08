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

# Загрузка модели
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
).to(device)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
print("✅ Mistral-7B загружена!")


def extract_json(text):
    text = text.strip()
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Поиск всех блоков JSON по скобкам
    results = []
    brace_stack = []
    start_idx = None

    for i, char in enumerate(text):
        if char == '{':
            if start_idx is None:
                start_idx = i
            brace_stack.append('{')
        elif char == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    results.append(text[start_idx:i+1].strip())
                    start_idx = None

    # Возвращаем последний валидный блок (финальный ответ)
    return results[-1] if results else None


def clean_json_keys(json_data):
    if isinstance(json_data, dict):
        return {k.strip(): clean_json_keys(v) for k, v in json_data.items()}
    elif isinstance(json_data, list):
        return [clean_json_keys(item) for item in json_data]
    return json_data


def process_text_with_mistral(text: str, prompt_type: str, filename: str = "Без названия"):
    try:
        with open(f"prompts/{prompt_type}_prompt.txt", encoding="utf-8") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        raise ValueError(f"❌ Промт prompts/{prompt_type}_prompt.txt не найден")

    safe_text = text.replace("{", "{{").replace("}", "}}")
    prompt = prompt_template.replace("{text}", safe_text)

    result = generator(
        prompt,
        max_new_tokens=1100,
        temperature=0.5,
        top_p=0.95,
        repetition_penalty=1.1,
        do_sample=True
    )[0]["generated_text"]

    print("🔍 Ответ модели:\n", result)
    extracted_json = extract_json(result)
    if not extracted_json:
        return {
            "type": prompt_type,
            "title": filename.rsplit(".", 1)[0],
            "questions": []
        }

    try:
        structured_data = json.loads(extracted_json)
        if isinstance(structured_data, list) and len(structured_data) > 0:
            structured_data = structured_data[0]
    except json.JSONDecodeError:
        return {
            "type": prompt_type,
            "title": filename.rsplit(".", 1)[0],
            "questions": []
        }

    structured_data = clean_json_keys(structured_data)
    structured_data.setdefault("type", prompt_type)

    # Название из файла, если модель не вернула строку
    title_val = structured_data.get("title")
    if not isinstance(title_val, str) or not title_val.strip():
        structured_data["title"] = filename.rsplit(".", 1)[0]

    structured_data.setdefault("questions", [])
    return structured_data
