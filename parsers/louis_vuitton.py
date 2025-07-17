from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup, Tag
import time
import re
import requests
import os

def get_eur_rub_rate():
    try:
        resp = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=5)
        data = resp.json()
        return float(data['Valute']['EUR']['Value'])
    except Exception:
        return None

def calc_rub_price(eur_price: float | None, eur_rub_rate: float | None) -> int | None:
    if eur_price is None or eur_rub_rate is None:
        return None
    rub = (eur_rub_rate + 9) * eur_price * 1.25
    return int(rub)

def parse(url: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=fr')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    service = Service('/usr/bin/chromedriver' if os.path.exists('/usr/bin/chromedriver') else '/Users/pavellapin/Downloads/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "lxml")
    # Название: ищем h1, h2, meta, title
    title = None
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(strip=True)
    if not title:
        meta_title = soup.find("meta", property="og:title")
        if meta_title and meta_title.get("content"):
            title = meta_title["content"]
    if not title:
        title = soup.title.string.strip() if soup.title else None
    if not title:
        print("[LouisVuitton] Не найдено название! Фрагмент:", soup.prettify()[:2000])
        title = "Не удалось найти название"
    # Цена: ищем span с € или div с ценой
    price = None
    price_tag = soup.find(lambda tag: tag.name in ["span", "div"] and tag.get_text().strip().endswith("€"))
    if price_tag:
        price = price_tag.get_text(strip=True)
    if not price:
        # Иногда цена в meta
        meta_price = soup.find("meta", property="product:price:amount")
        if meta_price and meta_price.get("content"):
            price = meta_price["content"] + " €"
    if not price:
        print("[LouisVuitton] Не найдена цена! Фрагмент:", soup.prettify()[:2000])
        price = "Не удалось найти цену"
    # Фото (главное изображение)
    img_url = None
    img_tag = soup.find("img", class_="lv-product-gallery__main-image")
    if not (img_tag and isinstance(img_tag, Tag)):
        img_tag = soup.find("img", {"data-testid": "product-image-main"})
    if not (img_tag and isinstance(img_tag, Tag)):
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = og_img["content"]
    if img_tag and isinstance(img_tag, Tag):
        img_url = img_tag.get("src")
    if img_url and isinstance(img_url, str) and img_url.startswith("//"):
        img_url = "https:" + img_url
    eur_price = None
    m = re.search(r"([\d\s]+)[€]", price)
    if m:
        eur_price = float(m.group(1).replace(" ", ""))
    eur_rub_rate = get_eur_rub_rate()
    rub_price = calc_rub_price(eur_price, eur_rub_rate) if eur_price else None
    return {
        "title": title,
        "price": price,
        "img_url": img_url,
        "rub_price": rub_price
    } 