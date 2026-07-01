from .base import get_page, clean_text, parse_salary

SOURCE_NAME = 'habr.com'
BASE_URL = 'https://career.habr.com'

def fetch(keyword='Python'):
    url = f'{BASE_URL}/vacancies?q={keyword}'
    result = []
    
    print(f"🌐 Парсинг Habr: {keyword} ...")
    
    soup = get_page(url)
    if soup is None:
        return result
    
    cards = soup.find_all('div', class_='vacancy-card')
    if not cards:
        print(f"⚠️ Не найдены карточки на Habr")
        return result
    
    for card in cards:
        title_tag = card.find('a', class_='vacancy-card__title-link')
        if not title_tag:
            continue
        
        company_name = 'Неизвестно'
        company_container = card.find('div', class_='vacancy-card__company')
        if company_container:
            company_link = company_container.find('a')
            if company_link:
                company_name = clean_text(company_link.text)
            else:
                company_name = clean_text(company_container.text)
        
        if company_name == 'Неизвестно' or not company_name:
            company_tag = card.find('div', class_='vacancy-card__company-title')
            if company_tag:
                company_name = clean_text(company_tag.text)
        
        salary_tag = card.find('div', class_='vacancy-card__salary')
        salary = parse_salary(salary_tag.text if salary_tag else None)
        
        href = title_tag.get('href', '')
        if href.startswith('/'):
            href = BASE_URL + href
        
        result.append({
            'company': company_name,
            'title': clean_text(title_tag.text),
            'salary': salary,
            'url': href,
            'source': SOURCE_NAME
        })
    
    print(f"✅ Habr: найдено {len(result)} вакансий")
    return result