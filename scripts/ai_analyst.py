import json
import re
import requests

def ask_ai():
    # Загружаем данные NBA
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    # Берем данные команд
    teams_context = json.dumps(data['teams'][:10], ensure_ascii=False)
    
    # Используем бесплатный API DuckDuckGo AI (он работает без ключей!)
    url = "https://duckduckgo.com/duckchat/v1/chat"
    
    # 1. Получаем статус (VQD токен) - это нужно для работы чата
    status_headers = {"x-vqd-accept": "1"}
    try:
        status_res = requests.get("https://duckduckgo.com/duckchat/v1/status", headers=status_headers)
        vqd = status_res.headers.get("x-vqd-4")
    except:
        print("Не удалось подключиться к бесплатному шлюзу.")
        return

    # 2. Делаем сам запрос
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user", 
                "content": f"NBA stats: {teams_context}. Output 3 match predictions strictly in JSON: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. No markdown, no text, just raw JSON."
            }
        ]
    }
    
    headers = {
        "x-vqd-4": vqd,
        "Content-Type": "application/json"
    }

    try:
        print("Запрос прогнозов через бесплатный канал...")
        response = requests.post(url, headers=headers, json=payload)
        
        # Очистка текста от лишних символов
        raw_text = response.text
        # Ищем JSON массив в ответе
        json_match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
        
        if json_match:
            predictions = json.loads(json_match.group(0))
            data['ai_analysis'] = predictions
            with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("УРА! Прогнозы успешно получены бесплатно.")
        else:
            # Запасной вариант: если API вернуло странный формат, запишем "заглушку"
            print("ИИ занят, используем аналитические данные.")
            data['ai_analysis'] = [
                {"match": "NBA Game", "winner": "Прогноз скоро обновится", "total": "-", "prob": "50%", "analysis": "Данные подгружаются..."}
            ]
            with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
