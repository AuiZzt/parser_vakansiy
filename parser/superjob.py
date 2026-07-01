"""
Парсер вакансий с SuperJob (Уфа) с защитой от блокировки
"""
import time
import random
from .base import get_page, clean_text, parse_salary

SOURCE_NAME = 'superjob.ru'
BASE_URL = 'https://ufa.superjob.ru'

def fetch(keyword='Python'):
    """Парсинг вакансий с SuperJob (Уфа)"""
    url = f'{BASE_URL}/vacancy/search/?keywords={keyword}'
    result = []
    
    print(f"🌐 Парсинг SuperJob: {keyword} ...")
    
    # Случайная задержка перед запросом
    time.sleep(random.uniform(1, 3))
    
    soup = get_page(url)
    if soup is None:
        return result
    
    cards = soup.find_all('div', class_='f-test-search-result-item')
    if not cards:
        print(f"⚠️ Не найдены карточки на SuperJob")
        return result
    
    for card in cards:
        vacancy_div = card.find('div', class_=lambda x: x and 'f-test-vacancy-item' in x)
        if not vacancy_div:
            continue
        
        title_tag = vacancy_div.find('a', class_=lambda x: x and 'f-test-link-' in x)
        if not title_tag:
            title_tag = vacancy_div.find('a', href=lambda x: x and 'superjob.ru/vakansii/' in x)
        
        company_tag = vacancy_div.find('span', class_='f-test-text-vacancy-item-company-name')
        if company_tag:
            company_link = company_tag.find('a')
            company_name = clean_text(company_link.text) if company_link else clean_text(company_tag.text)
        else:
            company_name = 'Неизвестно'
        
        salary_tag = vacancy_div.find('span', class_='f-test-text-company-item-salary')
        salary = clean_text(salary_tag.text) if salary_tag else 'Не указана'
        
        if title_tag:
            href = title_tag.get('href', '')
            if href.startswith('/'):
                href = 'https://www.superjob.ru' + href
            
            result.append({
                'company': company_name,
                'title': clean_text(title_tag.text),
                'salary': salary,
                'url': href,
                'source': SOURCE_NAME
            })
    
    print(f"✅ SuperJob: найдено {len(result)} вакансий")
    return result