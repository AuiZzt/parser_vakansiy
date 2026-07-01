#!/usr/bin/env python3
"""
Главный скрипт для запуска парсеров (Уфа + Habr)
Источники: Habr, SuperJob, Работа.ру
"""
import json
import time
import random
from parser import habr, superjob, rabota

KEYWORDS = ['Python', 'Java', 'JavaScript']

PARSERS = [
    ('Habr', habr.fetch),
    ('SuperJob', superjob.fetch),
    ('Работа.ру', rabota.fetch),
]

def main():
    all_vacancies = []
    
    print("🚀 ЗАПУСК ПАРСЕРА ВАКАНСИЙ")
    print("=" * 40)
    print("⚠️  Источники: Habr (все регионы), SuperJob (Уфа), Работа.ру (Уфа)")
    print("⚠️  Habr не фильтрует по региону — показывает вакансии со всей России")
    print("=" * 40)
    
    for keyword in KEYWORDS:
        print(f"\n📝 Обработка запроса: {keyword}")
        print("=" * 40)
        
        for name, parser_func in PARSERS:
            print(f"\n--- {name} ---")
            vacancies = parser_func(keyword)
            all_vacancies.extend(vacancies)
            
            delay = random.uniform(3, 6)
            print(f"⏳ Пауза {delay:.1f} секунд...")
            time.sleep(delay)
        
        delay = random.uniform(5, 10)
        print(f"⏳ Пауза {delay:.1f} секунд перед следующим запросом...")
        time.sleep(delay)
    
    unique = {}
    for v in all_vacancies:
        if v['url']:
            unique[v['url']] = v
    final_list = list(unique.values())
    
    print("\n" + "=" * 40)
    print(f"✅ Итого уникальных вакансий: {len(final_list)}")
    
    if final_list:
        final_list.sort(key=lambda x: x['company'])
        
        with open('vacancies.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)
        print("📁 Данные сохранены в vacancies.json")
        
        print(f"\n📊 Статистика по источникам:")
        sources = {}
        for v in final_list:
            src = v.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
        for src, count in sources.items():
            print(f"  {src}: {count} вакансий")
        
        print(f"\n📊 Первые 5 вакансий:")
        for i, v in enumerate(final_list[:5], 1):
            print(f"  {i}. {v['title']} - {v['company']} ({v['source']})")
    else:
        print("⚠️ Вакансий не найдено.")

if __name__ == '__main__':
    main()