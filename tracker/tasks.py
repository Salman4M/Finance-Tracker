import requests
from tracker.models import PriceHistory
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC


# def fetch_asset_data(symbol='bitcoin'):
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
#     response = requests.get(url)
#     data = response.json()
#     return data[symbol]['usd']

def fetch_stock_price(symbol):
    options=webdriver.ChromeOptions()
    options.add_argument('--headless')# it make chrome run in headless mode
    options.add_argument('--no-sandbox')# it make chrome run in a sandbox
    options.add_argument('--disable-dev-shm-usage') #it make chrome run in a container
    service=Service(executable_path=r"C:\Users\Salman\Desktop\chromedriver.exe")
    driver=webdriver.Chrome(service=service,options=options)

    try:
        url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
        driver.get(url)

        price_element=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.YMlKec.fxKbKc")))

        price_text=price_element.text.strip()
        price=float(price_text.replace(',',''))
        return price
    finally:
        driver.quit()   
    




@shared_task
def fetch_crypto_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    try:
        data = requests.get(url, timeout=10).json()
        for symbol in data:
            PriceHistory.objects.create(
                symbol=symbol.upper(),
                price=data[symbol]['usd']
            )
        print("Prices saved successfully.")
    except Exception as e:
        print(f"Error fetching prices: {e}")

    try:
        for symbol in ["AAPL", "MSFT"]:
            price = fetch_stock_price(symbol)
            PriceHistory.objects.create(
                asset_id=2,  # replace with real Asset mapping
                price=price
            )
            print(f"{symbol} saved: {price}")
    except Exception as e:
        print(f"Stock fetch error: {e}")
