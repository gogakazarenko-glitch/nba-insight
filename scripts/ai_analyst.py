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
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/nba-dashboard", 
        "X-Title": "NBA AI Analyst"
    }
    
    payload = {
        "model": "huggingfaceh4/zephyr-7b-beta:free", # Самая живучая бесплатная модель
        "messages": [
            {
                "role": "user", 
                "content": f"NBA stats: {teams_context}. Output 3 match predictions as JSON: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. JSON only!"
            }
        ],
        "temperature": 0.1
    }

    try:
        print("Отправка запроса в OpenRouter (Zephyr Free)...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        result = response.json()

        if 'choices' in result:
            raw_text = result['choices'][0]['message']['content']
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            
            if json_match:
                data['ai_analysis'] = json.loads(json_match.group(0))
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("ЕСТЬ! Наконец-то данные получены.")
            else:
                print(f"JSON не найден. ИИ ответил: {raw_text[:150]}")
        else:
            # Если и это упадет, попробуем просто 'openrouter/auto'
            print(f"Ошибка OpenRouter: {result}")
            if 'error' in result and result['error'].get('code') == 404:
                print("Похоже, бесплатные модели временно отключены. Попробуем позже или сменим провайдера.")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
