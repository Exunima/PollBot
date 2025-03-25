from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Путь для хранения модели
cache_dir = "F:/BOT_TELEGRAM/PollBot/Mistral-7B"

# Настройка квантования 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16"
)

# Загружаем токенизатор и модель с Hugging Face
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, token=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    cache_dir=cache_dir,
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
)

print("✅ Mistral-7B-Instruct-v0.2 загружена в:", cache_dir)
