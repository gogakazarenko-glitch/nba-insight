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
    
    prompt = f"NBA Data: {teams_context}. Напиши 3 прогноза на сегодня. Ответ дай ТОЛЬКО в формате JSON списка объектов с полями: match, winner, total, prob, analysis."

    # Самый надежный список моделей на текущий момент
    model_variants = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    success = False
    for model in model_variants:
        print(f"Пробую модель: {model}...")
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()

            if 'candidates' in result:
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                predictions = json.loads(ai_text)
                
                # Если ИИ вернул словарь с ключом, вытаскиваем список
                if isinstance(predictions, dict) and 'predictions' in predictions:
                    predictions = predictions['predictions']
                
                data['ai_analysis'] = predictions
                success = True
                break
            else:
                print(f"Модель {model} не ответила: {result.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Ошибка при вызове {model}: {e}")

    if success:
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("УРА! Данные успешно обновлены.")
    else:
        print("К сожалению, ни одна модель не подошла. Проверь API ключ в Google AI Studio.")

if __name__ == "__main__":
    ask_ai()
