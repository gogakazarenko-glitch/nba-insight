import json
import random

def ask_ai():
    try:
        with open('data/final_stats.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return

    # Берем первые 10 команд из нашего списка
    teams = data.get('teams', [])
    if len(teams) < 2:
        return

    # Генерируем 3 прогноза на основе реальной статистики команд
    predictions = []
    
    # Берем случайные пары из топ-10
    random_teams = random.sample(teams[:10], 6)
    
    for i in range(0, 6, 2):
        t1 = random_teams[i]
        t2 = random_teams[i+1]
        
        # Считаем, кто сильнее по проценту побед (Win %)
        w1 = float(t1['win_pct'].replace('%', ''))
        w2 = float(t2['win_pct'].replace('%', ''))
        
        winner = t1['team'] if w1 > w2 else t2['team']
        prob = max(w1, w2)
        
        predictions.append({
            "match": f"{t1['team']} vs {t2['team']}",
            "winner": winner,
            "total": f"ТБ {random.randint(215, 230)}.5",
            "prob": f"{int(prob)}%",
            "analysis": f"Анализ основан на текущем винрейте: {t1['team']} ({t1['win_pct']}) против {t2['team']} ({t2['win_pct']})."
        })

    # Записываем результат
    data['ai_analysis'] = predictions
    with open('data/final_stats.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("УРА! Математический прогноз успешно сформирован.")

if __name__ == "__main__":
    ask_ai()
