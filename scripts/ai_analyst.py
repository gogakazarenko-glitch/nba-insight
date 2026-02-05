import os
import json
import requests

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Ошибка: Ключ API не найден в Secrets!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("Ошибка: Файл final_stats.json не найден.")
        return

    teams_info = json.dumps(data['teams'], ensure_ascii=False)
    
    prompt = f"""
    Ты — эксперт NBA. Данные команд: {teams_info}.
    Проанализируй форму. Выдай 3 прогноза на сегодня.
    Для каждого: Победитель (Moneyline), Тотал (Больше/Меньше), Вероятность % и детальная ПРИЧИНА.
    Ответ дай ТОЛЬКО в формате JSON:
    {{
      "predictions": [
        {{
          "match": "Team A vs Team B",
          "winner": "Winner Name",
          "total": "O/U value",
          "prob": "XX%",
          "reason": "Reasoning in Russian"
        }}
      ]
    }}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        response = requests.post(url, json=payload)
        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        ai_data = json.loads(ai_text)
        data['ai_analysis'] = ai_data['predictions']
        
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("ИИ-анализ успешно добавлен.")
    except Exception as e:
        print(f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    ask_ai()
