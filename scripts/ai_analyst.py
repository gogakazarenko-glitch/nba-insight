import os
import json
import requests

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return

    # Берем данные для контекста
    teams_info = json.dumps(data['teams'], ensure_ascii=False)
    
    prompt = f"""
    Ты — ведущий аналитик NBA и эксперт по ставкам. Используй эти данные: {teams_info}.
    Твоя задача: Составить глубокий аналитический отчет на сегодня.
    
    Для каждого из 3-х ключевых матчей дня:
    1. Проанализируй разницу в Power Rating.
    2. Оцени Moneyline (победитель) и обоснование.
    3. Дай прогноз на Тотал (Over/Under) исходя из темпа команд.
    4. Напиши подробный аналитический разбор (почему именно такой исход).
    
    Ответ дай строго в формате JSON:
    {{
      "predictions": [
        {{
          "match": "Команда А vs Команда Б",
          "winner": "Название",
          "total": "Например: Больше 225.5",
          "prob": "Процент уверенности",
          "analysis": "Здесь напиши 3-4 глубоких предложения с цифрами и логикой"
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
        res_json = response.json()
        ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
        ai_data = json.loads(ai_text)
        
        # Сохраняем расширенный анализ
        data['ai_analysis'] = ai_data['predictions']
        
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Глубокая аналитика добавлена.")
    except Exception as e:
        print(f"Ошибка ИИ: {e}")

if __name__ == "__main__":
    ask_ai()
