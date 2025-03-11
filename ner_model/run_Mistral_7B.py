from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "mistralai/Mistral-7B-Instruct-v0.2"
cache_dir = "F:/BOT_TELEGRAM/PollBot/Mistral-7B"

tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    cache_dir=cache_dir,
    device_map="auto",
    load_in_4bit=True,  # 4-bit квантование (чтобы влезло в 6GB VRAM)
    use_auth_token=True
)

print("✅ Mistral-7B-Instruct-v0.2 загружена в:", cache_dir)
