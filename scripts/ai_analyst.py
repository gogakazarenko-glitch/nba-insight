import os
import json
import requests

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ОШИБКА: Ключ GEMINI_API_KEY не найден!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return

    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    
    prompt = f"Данные NBA: {teams_context}. На основе рейтингов составь 3 прогноза. Дай ответ СТРОГО в формате JSON списка объектов с полями: match, winner, total, prob, analysis. Только чистый JSON."

    # Пробуем универсальную модель gemini-pro, которая есть во всех версиях API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if 'error' in result:
            # Если gemini-pro тоже не найдена, пробуем последнюю попытку с явным указанием 1.5
            print(f"Попытка 1 (gemini-pro) не удалась: {result['error'].get('message')}")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

        if 'candidates' not in result:
            print(f"Не удалось получить ответ от ИИ. Ответ сервера: {result}")
            return

        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Очистка от Markdown
        clean_json = ai_text.strip()
        if clean_json.startswith('```'):
            clean_json = clean_json.split('```')[1]
            if clean_json.startswith('json'):
                clean_json = clean_json[4:]
        
        predictions = json.loads(clean_json.strip())
        data['ai_analysis'] = predictions
        
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("УРА! Прогнозы успешно записаны.")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
