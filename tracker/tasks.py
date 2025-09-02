import requests
from tracker.models import Asset, PriceHistory,Alert
from celery import shared_task
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


# def fetch_asset_data(symbol='bitcoin'):
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
#     response = requests.get(url)
#     data = response.json()
#     return data[symbol]['usd']

# def fetch_stock_price(symbol):
#     options=webdriver.ChromeOptions()
#     options.add_argument('--headless')# it make chrome run in headless mode
#     options.add_argument('--no-sandbox')# it make chrome run in a sandbox
#     options.add_argument('--disable-dev-shm-usage') #it make chrome run in a container
#     service=Service(executable_path=r"C:\Users\Salman\Desktop\chromedriver.exe")
#     driver=webdriver.Chrome(service=service,options=options)

#     try:
#         url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
#         driver.get(url)

#         price_element=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.YMlKec.fxKbKc")))

#         price_text=price_element.text.strip()
#         price=float(price_text.replace(',',''))
#         return price
#     finally:
#         driver.quit()   


def fetch_stock_price_bs(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Yahoo Finance: price is in <fin-streamer data-field="regularMarketPrice">
        price_element = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
        if price_element:
            price_text = price_element.text.strip().replace(",", "")
            return float(price_text)
        else:
            raise ValueError(f"Price not found for {symbol}")
    except Exception as e:
        return f"Error fetching price for {symbol}: {e}"
    


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
            price = fetch_stock_price_bs(symbol)
            PriceHistory.objects.create(
                symbol=symbol.upper(),
                price=price
            )
            print(f"{symbol} saved: {price}")
    except Exception as e:
        print(f"Stock fetch error: {e}")




def get_latest_prices():
    results={}
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    data=requests.get(url,timeout=10).json()
    for symbol in data:
        results[symbol.upper()]=data[symbol]['usd']

    return results


def alert_price_drop_or_rise(results):
    for symbol,price in results.items():
        alerts=Alert.objects.filter(asset__symbol=symbol.upper(), trigger=False)
        for alert in alerts:
            try:
                amount=Decimal(alert.asset.amount)
                current_price = Decimal(price)
                price=Decimal(amount*current_price)
                target_price = Decimal(alert.target_price)

                send = False
                if alert.condition == 'Above' and price > target_price:
                    send = True
                elif alert.condition == 'Below' and price < target_price:
                    send = True

                if send:
                    send_mail(
                        "Update on your Asset",
                        f"The latest price for {symbol} is {price}.",
                        settings.DEFAULT_FROM_EMAIL,
                        [alert.user.email],
                    )
                    alert.trigger = True
                    alert.save(update_fields=["trigger"])

            except Exception as e:
                print(f"Error processing alert {alert.id} for {symbol}: {e}")


@shared_task
def check_prices():
    latest_prices = get_latest_prices()
    alert_price_drop_or_rise(latest_prices)

# def alert_price_drop_or_rise_symbols():
#     symbols=(
#         Alert.objects.filter(trigger=False).values_list('asset__symbol', flat=True).distinct()
#     )
#     for symbol in symbols:
#         alert_price_drop_or_rise(symbol)
