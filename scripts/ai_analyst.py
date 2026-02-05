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
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    teams_context = json.dumps(data['teams'][:10], ensure_ascii=False)
    
    # ПРАВИЛЬНЫЙ URL для Router (без названия модели в адресе!)
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct", 
        "messages": [
            {"role": "user", "content": f"NBA stats: {teams_context}. Output 3 match predictions as JSON list. Format: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. No markdown, no intro."}
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        print("Отправка запроса в чистый Router...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            raw_text = result['choices'][0]['message']['content']
            
            # Чистим от возможных Markdown-кавычек ```json
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                data['ai_analysis'] = json.loads(json_match.group(0))
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("ПОБЕДА! Прогнозы записаны.")
            else:
                print(f"JSON не найден. ИИ прислал: {raw_text[:100]}")
        else:
            print(f"Ошибка сервера (Статус {response.status_code}): {response.text}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
