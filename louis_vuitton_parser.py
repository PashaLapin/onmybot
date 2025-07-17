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

def parse_louis_vuitton_product(url: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=fr')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("h1", class_="lv-product-title__main")
    title = title_tag.get_text(strip=True) if title_tag else "Не удалось найти название"

    price_tag = soup.find("span", class_="lv-product-price__amount")
    price = price_tag.get_text(strip=True) if price_tag else "Не удалось найти цену"
    eur_price = None
    if price:
        match = re.search(r"([\d\s]+)[^\d]*€", price)
        if match:
            eur_price = float(match.group(1).replace(" ", ""))

    img_url = None
    img_tag = soup.find("img", class_="lv-product-gallery__main-image")
    if not (img_tag and isinstance(img_tag, Tag)):
        img_tag = soup.find("img", {"data-testid": "product-image-main"})
    if img_tag and isinstance(img_tag, Tag):
        img_url = img_tag.get("src")
    if img_url and isinstance(img_url, str) and img_url.startswith("//"):
        img_url = "https:" + img_url

    eur_rub_rate = get_eur_rub_rate()
    rub_price = calc_rub_price(eur_price, eur_rub_rate)

    return {
        "title": title,
        "price": price,
        "img_url": img_url,
        "rub_price": rub_price,
    }

if __name__ == "__main__":
    url = "https://fr.louisvuitton.com/fra-fr/produits/cabas-onthego-mm-mon-monogram-monogram-nvprod6090110v/P01898?personalizationId=MAJDWAUE"
    data = parse_louis_vuitton_product(url)
    print(data) 