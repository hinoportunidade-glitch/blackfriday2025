import csv
import sqlite3
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from send_email import send_alert
from dotenv import load_dotenv

load_dotenv()

# Banco de dados
conn = sqlite3.connect('prices.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS prices (date TEXT, product TEXT, price REAL, url TEXT)''')
conn.commit()

def get_price(page, url):
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(8)
    
    price = None
    # Amazon
    if 'amazon.com.br' in url:
        try:
            price_text = page.locator("//span[contains(@class,'a-price-whole')]").first.inner_text() + page.locator("//span[contains(@class,'a-price-fraction')]").first.inner_text()
            price = float(price_text.replace('.', '').replace(',', '.'))
        except:
            try:
                price_text = page.locator("//span[@class='a-offscreen']").first.inner_text()
                price = float(price_text.replace('R$', '').replace('.', '').replace(',', '.').strip())
            except:
                pass
    
    # Magazine Luiza
    elif 'magazineluiza' in url:
        try:
            price_text = page.locator("span[data-testid='price-value']").first.inner_text()
            price = float(price_text.replace('R$', '').replace('.', '').replace(',', '.').strip())
        except:
            pass
    
    # Kabum
    elif 'kabum' in url:
        try:
            price_text = page.locator("//h4[contains(text(),'R$')]/b").first.inner_text()
            price = float(price_text.replace('R$', '').replace('.', '').replace(',', '.').strip())
        except:
            pass
    
    return price

def monitor():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()

        with open('products.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nome = row['nome']
                url = row['url']
                preco_desejado = float(row['preco_desejado'])
                desconto_min = int(row['desconto_minimo'])

                print(f"Verificando: {nome}")
                price = get_price(page, url)

                if price and price > 0:
                    c.execute("INSERT INTO prices VALUES (?,?,?,?)", 
                              (datetime.now().strftime("%Y-%m-%d %H:%M"), nome, price, url))
                    conn.commit()

                    # Preço antigo
                    c.execute("SELECT price FROM prices WHERE product=? ORDER BY rowid DESC LIMIT 1 OFFSET 1", (nome,))
                    old = c.fetchone()

                    if old:
                        antigo = old[0]
                        desconto = ((antigo - price) / antigo) * 100
                        if price <= preco_desejado or desconto >= desconto_min:
                            msg = f"""BLACK FRIDAY ALERTA
Produto: {nome}
Preço: R$ {price:,.2f}
Desconto: {desconto:.1f}%
Era: R$ {antigo:,.2f}
{url}"""
                            send_alert(msg)

        browser.close()

if __name__ == "__main__":
    print("Robô Black Friday iniciado!")
    while datetime.now() < datetime(2025, 12, 1):
        monitor()
        print(f"{datetime.now()} - Próxima verificação em 20 minutos...")
        time.sleep(20 * 60)
