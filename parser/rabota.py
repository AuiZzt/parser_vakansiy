from .base import get_page, clean_text, parse_salary

SOURCE_NAME = 'rabota.ru'
BASE_URL = 'https://ufa.rabota.ru'

def fetch(keyword='Python'):
    url = f'{BASE_URL}/vacancy/?query={keyword}'
    result = []
    
    print(f"🌐 Парсинг Работа.ру: {keyword} ...")
    
    soup = get_page(url)
    if soup is None:
        return result
    
    cards = soup.find_all('article', class_='vacancy-preview-card')
    if not cards:
        cards = soup.find_all('div', class_='vacancy-preview-card')
    
    if not cards:
        print(f"⚠️ Не найдены карточки на Работа.ру")
        return result
    
    for card in cards:
        title_tag = card.find('h3', class_='vacancy-preview-card__title')
        if title_tag:
            title_link = title_tag.find('a')
        else:
            title_link = card.find('a', href=lambda x: x and '/vacancy/' in x)
        
        if not title_link:
            continue
        
        company_tag = card.find('span', class_='vacancy-preview-card__company-name')
        if company_tag:
            company_link = company_tag.find('a')
            company_name = clean_text(company_link.text) if company_link else clean_text(company_tag.text)
        else:
            company_name = 'Неизвестно'
        
        salary_tag = card.find('div', class_='vacancy-preview-card__salary')
        if salary_tag:
            salary_link = salary_tag.find('a')
            salary = clean_text(salary_link.text) if salary_link else clean_text(salary_tag.text)
        else:
            salary = 'Не указана'
        
        href = title_link.get('href', '')
        if href.startswith('/'):
            href = 'https://ufa.rabota.ru' + href
        
        place_text = ''
        place_tag = card.find('div', class_='vacancy-preview-location')
        if place_tag:
            place_text = clean_text(place_tag.text)
        
        is_ufa = False
        if 'Уфа' in place_text or 'Уфе' in place_text:
            is_ufa = True
        
        if not is_ufa and 'ufa' in href:
            is_ufa = True
        
        if is_ufa:
            result.append({
                'company': company_name,
                'title': clean_text(title_link.text),
                'salary': salary,
                'url': href,
                'source': SOURCE_NAME
            })
    
    print(f"✅ Работа.ру: найдено {len(result)} вакансий (только Уфа)")
    return result