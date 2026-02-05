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

    # Берем топ-15 команд для анализа
    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    
    prompt = f"Данные NBA: {teams_context}. На основе рейтингов составь 3 прогноза. Дай ответ СТРОГО в формате JSON списка объектов с полями: match, winner, total, prob, analysis. Только чистый JSON, без лишнего текста."

    # Используем версию v1 и модель gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
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
            print(f"Ошибка от Google: {result['error'].get('message', 'Unknown error')}")
            return

        if 'candidates' not in result:
            print(f"Нет кандидатов в ответе. Ответ: {result}")
            return

        # Извлекаем текст
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Очистка от Markdown (если ИИ добавил ```json)
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
