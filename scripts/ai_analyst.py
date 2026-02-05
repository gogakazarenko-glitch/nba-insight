import os
import json
import requests
import re

def ask_ai():
    # Используем тот же секрет, куда ты вставишь ключ DeepSeek
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ОШИБКА: Ключ не найден!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Файл данных не найден: {e}")
        return

    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    
    prompt = f"Данные NBA: {teams_context}. Напиши 3 прогноза на сегодня. Ответ дай СТРОГО в формате JSON списка объектов: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. Пиши только JSON."

    # URL для DeepSeek
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты профессиональный каппер и аналитик NBA. Выдаешь только JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if 'choices' in result:
            raw_text = result['choices'][0]['message']['content']
            
            # Находим JSON в тексте
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                data['ai_analysis'] = json.loads(json_match.group(0))
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("УРА! DeepSeek успешно проанализировал матчи.")
            else:
                print(f"JSON не найден в ответе: {raw_text}")
        else:
            print(f"Ошибка DeepSeek API: {result}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
