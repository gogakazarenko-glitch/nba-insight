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
        print(f"Файл не найден: {e}")
        return

    teams_context = json.dumps(data['teams'][:12], ensure_ascii=False)
    
    # URL OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemini-2.0-flash-exp:free", # БЕСПЛАТНАЯ и мощная модель
        "messages": [
            {
                "role": "user", 
                "content": f"NBA Data: {teams_context}. Output 3 predictions in JSON: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. Only JSON!"
            }
        ]
    }

    try:
        print("Отправка запроса в OpenRouter...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()

        if 'choices' in result:
            raw_text = result['choices'][0]['message']['content']
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            
            if json_match:
                data['ai_analysis'] = json.loads(json_match.group(0))
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("УРА! OpenRouter (Gemini Free) всё сделал.")
            else:
                print(f"JSON не найден. Ответ: {raw_text[:100]}")
        else:
            print(f"Ошибка OpenRouter: {result}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
