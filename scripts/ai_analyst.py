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

    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    
    # Очень строгий промпт, чтобы ИИ не писал лишнего
    prompt = f"Данные NBA: {teams_context}. Напиши 3 прогноза на сегодня. Ответ дай СТРОГО в формате JSON списка объектов: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. Напиши только JSON и ничего больше."

    model = "gemini-1.5-flash" # Самая быстрая модель
    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()

        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Чистим текст от возможных "```json" и лишних слов
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
                predictions = json.loads(clean_json)
                
                data['ai_analysis'] = predictions
                
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("УРА! Прогнозы успешно записаны в файл.")
            else:
                print(f"ИИ выдал текст, но в нем нет JSON: {raw_text}")
        else:
            print(f"Ошибка API: {result.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        print(f"Ошибка парсинга или запроса: {e}")

if __name__ == "__main__":
    ask_ai()
