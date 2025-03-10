from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

# Путь для хранения модели
local_dir = "F:/BOT_TELEGRAM/PollBot/deepseek_models"

# Скачиваем модель (если ещё не скачана)
snapshot_download(
    repo_id="deepseek-ai/deepseek-llm-7b-chat",
    local_dir=local_dir
)

# Настройки квантования 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="float16"
)

# Загружаем токенизатор и модель из локальной папки с квантованием
tokenizer = AutoTokenizer.from_pretrained(local_dir)
model = AutoModelForCausalLM.from_pretrained(
    local_dir,
    quantization_config=bnb_config,
    device_map="auto"
)

# Создаем пайплайн генерации
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto"
)

# Пример текста для генерации
prompt = "Какие функции есть у DeepSeek LLM? Объясни подробно."

# Генерируем ответ
result = generator(
    prompt,
    max_new_tokens=500,  # Дадим модели больше места для генерации
    temperature=0.7,  # Немного увеличиваем случайность
    top_p=0.9,  # Усредняем вероятности слов
    do_sample=True
)

print(result[0]["generated_text"])
