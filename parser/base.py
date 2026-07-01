import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_page(url, headers=None, timeout=20):
    if headers is None:
        headers = HEADERS.copy()
    
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f"❌ Ошибка загрузки {url}: {e}")
        return None

def clean_text(text):
    if not text:
        return ''
    return ' '.join(text.strip().split())

def parse_salary(salary_text):
    if not salary_text:
        return 'Не указана'
    return clean_text(salary_text)