import requests
import json
import os
from bs4 import BeautifulSoup

def get_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    stats = []

    if not os.path.exists('data'):
        os.makedirs('data')

    try:
        url = "https://www.teamrankings.com/nba/ranking/predictive-by-other"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        table = soup.find('table', {'class': 'datatable'})
        rows = table.find_all('tr')[1:31] # Четко 30 команд

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                stats.append({
                    "rank": cols[0].text.strip().replace('.', ''),
                    "team": cols[1].text.strip().split('(')[0].strip(),
                    "rating": cols[2].text.strip(),
                    "sos": cols[3].text.strip()
                })

        with open('data/final_stats.json', 'w', encoding='utf-8') as f:
            json.dump({"teams": stats}, f, ensure_ascii=False, indent=4)
        print("Базовые данные собраны успешно.")
    except Exception as e:
        print(f"Ошибка сбора данных: {e}")

if __name__ == "__main__":
    get_data()
