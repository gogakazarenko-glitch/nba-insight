import os
import json
import requests
import re

def ask_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ОШИБКА: Ключ не найден в Secrets!")
        return
    
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Файл данных не найден: {e}")
        return

    teams_context = json.dumps(data['teams'][:15], ensure_ascii=False)
    prompt = f"Данные NBA: {teams_context}. Напиши 3 прогноза на сегодня. Ответ дай СТРОГО в формате JSON списка объектов: [{{'match': '...', 'winner': '...', 'total': '...', 'prob': '...', 'analysis': '...'}}]. Только JSON."

    # Комбинации, которые мы будем пробовать
    attempts = [
        ("v1beta", "gemini-1.5-flash"),
        ("v1", "gemini-pro"),
        ("v1beta", "gemini-pro"),
        ("v1", "gemini-1.5-flash")
    ]

    success = False
    for api_version, model in attempts:
        print(f"Пробую: {api_version} | Модель: {model}...")
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model}:generateContent?key={api_key}"
        
        try:
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
            result = response.json()

            if 'candidates' in result:
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                
                if json_match:
                    data['ai_analysis'] = json.loads(json_match.group(0))
                    success = True
                    print(f"СРАБОТАЛО на {model} ({api_version})!")
                    break
            else:
                err_msg = result.get('error', {}).get('message', 'Unknown error')
                print(f"Не подошло: {err_msg[:50]}...")
        except Exception as e:
            print(f"Ошибка соединения: {e}")

    if success:
        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Файл успешно обновлен!")
    else:
        print("!!! КРИТИЧЕСКАЯ ОШИБКА: Ни одна модель не ответила. Пожалуйста, создай НОВЫЙ ключ в Google AI Studio.")

if __name__ == "__main__":
    ask_ai()
