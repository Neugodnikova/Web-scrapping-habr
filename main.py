import aiohttp
import asyncio
from bs4 import BeautifulSoup

# Ключевые слова для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL страницы со свежими статьями
BASE_URL = "https://habr.com/ru/articles/"

async def fetch_page(session, url):
    """
    Загружает HTML-страницу.
    """
    async with session.get(url) as response:
        return await response.text()

async def parse_article_content(session, article_url):
    """
    Загружает и анализирует содержимое статьи по URL.
    """
    html = await fetch_page(session, article_url)
    soup = BeautifulSoup(html, 'html.parser')

    # Извлекаем текст статьи
    article_body = soup.find("div", class_="tm-article-body")
    if article_body:
        return article_body.text.strip()
    return ""

async def parse_articles(session, html):
    """
    Парсит заголовки, ссылки, даты, анализирует превью и текст статей.
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all("article")

    preview_matches = []
    full_text_matches = []

    for article in articles:
        # Извлекаем заголовок и ссылку
        title_element = article.find("a", class_="tm-title__link")
        if title_element:
            title = title_element.text.strip()
            link = f"https://habr.com{title_element['href']}"
        else:
            continue

        # Извлекаем дату
        date_element = article.find("time")
        date = date_element["title"] if date_element else "Без даты"

        # Извлекаем превью текста
        preview_element = article.find("div", class_="article-formatted-body")
        preview_text = preview_element.text.strip() if preview_element else ""

        # Проверяем совпадения в превью
        if any(keyword.lower() in f"{title} {preview_text}".lower() for keyword in KEYWORDS):
            preview_matches.append(f"{date} – {title} – {link}")

        # Получаем полный текст статьи
        full_text = await parse_article_content(session, link)
        # Проверяем совпадения в полном тексте
        if any(keyword.lower() in f"{title} {full_text}".lower() for keyword in KEYWORDS):
            full_text_matches.append(f"{date} – {title} – {link}")

    return preview_matches, full_text_matches

async def main():
    """
    Основная функция: загружает страницу, ищет статьи, содержащие ключевые слова.
    """
    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, BASE_URL)
        preview_matches, full_text_matches = await parse_articles(session, html)

        # Вывод списка по превью
        print("Статьи, найденные по анализу превью:")
        if preview_matches:
            for article in preview_matches:
                print(article)
        else:
            print("Подходящих статей по анализу превью не найдено.")

        # Вывод списка по полному содержимому
        print("\nСтатьи, найденные по анализу полного текста статьи:")
        if full_text_matches:
            for article in full_text_matches:
                print(article)
        else:
            print("Подходящих статей по анализу полного текста статьи не найдено.")

if __name__ == "__main__":
    asyncio.run(main())
