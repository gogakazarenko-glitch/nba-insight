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

    # Берем топ команд для контекста
    teams_context = json.dumps(data['teams'][:12], ensure_ascii=False)
    
    # URL для чат-моделей (самый стабильный)
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {
                "role": "system", 
                "content": "Ты аналитик NBA. Твоя задача — выдать 3 прогноза на основе данных. Ответ должен быть СТРОГО в формате JSON списка объектов."
            },
            {
                "role": "user", 
                "content": f"Данные: {teams_context}. Напиши 3 прогноза в формате JSON: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. Пиши только чистый JSON без текста."
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.1 # Минимум фантазии, максимум точности
    }

    try:
        print("Отправка запроса в Chat Router...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # Если пришла ошибка (например, 503 или 429)
        if response.status_code != 200:
            print(f"Ошибка сервера (Статус {response.status_code}): {response.text}")
            return

        result = response.json()
        
        if 'choices' in result:
            raw_text = result['choices'][0]['message']['content']
            
            # Поиск JSON в тексте
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group(0))
                data['ai_analysis'] = predictions
                
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("УРА! Прогнозы получены и сохранены.")
            else:
                print(f"ИИ прислал текст без JSON: {raw_text}")
        else:
            print(f"Необычный ответ от API: {result}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
