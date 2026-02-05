import os
import json
import requests
import re

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ОШИБКА: Ключ не найден!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return

    teams_context = json.dumps(data['teams'][:10], ensure_ascii=False)
    
    # Используем базовый эндпоинт чата (он сам выберет модель)
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct", # Легкая и быстрая модель
        "messages": [
            {"role": "user", "content": f"NBA data: {teams_context}. Output 3 match predictions in STRICT JSON format only. Format: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. No conversation, no markdown, just JSON."}
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        print("Пробую получить прогнозы через универсальный Router...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"Ошибка (Статус {response.status_code}): {response.text}")
            # Если 404, попробуем еще один запасной путь прямо сейчас
            if response.status_code == 404:
                 print("Пробую альтернативный путь...")
                 url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct/v1/chat/completions"
                 response = requests.post(url, headers=headers, json=payload, timeout=60)

        result = response.json()
        if 'choices' in result:
            raw_text = result['choices'][0]['message']['content']
            
            # Ищем JSON
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                data['ai_analysis'] = json.loads(json_match.group(0))
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("ПОБЕДА! Данные получены.")
            else:
                print(f"Текст без JSON: {raw_text[:100]}")
        else:
            print(f"API ответил странно: {result}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
