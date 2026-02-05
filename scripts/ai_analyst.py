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
        print(f"Ошибка загрузки данных: {e}")
        return

    teams_context = json.dumps(data['teams'][:12], ensure_ascii=False)
    
    # Промпт для Llama
    prompt = f"System: Ты аналитик NBA. На основе этих данных: {teams_context} составь 3 прогноза. Дай ответ ТОЛЬКО в формате JSON списка: [{{'match': 'Команда1 - Команда2', 'winner': 'Победитель', 'total': 'ТБ/ТМ', 'prob': '85%', 'analysis': 'Кратко почему'}}] \nAssistant: ["

    # НОВЫЙ URL, который требует Hugging Face
    url = "https://router.huggingface.co/hf-inference/models/meta-llama/Llama-3.1-8B-Instruct"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1000,
            "return_full_text": False,
            "temperature": 0.7
        }
    }

    try:
        print("Отправка запроса в новый Router Hugging Face...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # Если модель еще загружается, HF может вернуть 503, добавим проверку
        if response.status_code == 503:
            print("Модель прогревается, подожди минуту и запусти снова.")
            return

        result = response.json()

        if isinstance(result, list) and 'generated_text' in result[0]:
            raw_text = "[" + result[0]['generated_text']
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group(0))
                data['ai_analysis'] = predictions
                with open('data/final_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("УРА! Прогнозы успешно записаны через новый API.")
            else:
                print(f"Не удалось найти JSON. Ответ: {raw_text[:100]}")
        else:
            print(f"Ошибка API: {result}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    ask_ai()
