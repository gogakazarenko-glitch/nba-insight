import os
import json
import requests

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ОШИБКА: Ключ GEMINI_API_KEY не найден в секретах Гитхаба!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return

    # Подготовка данных (топ-15 команд)
    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    
    prompt = f"Данные NBA: {teams_context}. На основе этих рейтингов составь 3 прогноза. Дай ответ СТРОГО в формате JSON списка объектов с полями: match, winner, total, prob, analysis. Только чистый JSON."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        })
        
        result = response.json()

        # Если Google вернул ошибку, мы увидим её в логах
        if 'error' in result:
            print(f"Гитхаб получил ошибку от Google: {result['error']['message']}")
            return

        if 'candidates' not in result:
            print(f"Странный ответ от ИИ (нет candidates). Полный ответ: {result}")
            return

        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Очистка текста от Markdown кавычек ```json ... ```
        clean_json = ai_text.replace('```json', '').replace('```', '').strip()
        predictions = json.loads(clean_json)
        
        data['ai_analysis'] = predictions
        
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Успех! Прогнозы записаны в файл.")

    except Exception as e:
        print(f"Общая ошибка в скрипте: {e}")

if __name__ == "__main__":
    ask_ai()
