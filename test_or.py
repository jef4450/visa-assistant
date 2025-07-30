import requests

API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost",  # keep as-is
    "X-Title": "OpenRouterTest"
}

payload = {
    "model": "openrouter/openai/gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of Germany?"}
    ]
}

res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

print("Status:", res.status_code)
print("Response:", res.text)
