import scrapy
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class RaiaSpider(scrapy.Spider):
    name = "raia"
    allowed_domains = ["www.drogaraia.com.br"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self):
        super().__init__()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def closed(self, reason):
        self.driver.quit()

    def start_requests(self):
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for prod in products:
            pid = prod['id']
            raw_slug = prod.get('raia_slug')
            if not raw_slug:
                continue

            slug = raw_slug.split('?')[0]
            if slug.endswith('.html'):
                slug = slug[:-5]

            url = f"https://www.drogaraia.com.br/{slug}.html"

            try:
                self.driver.get(url)
                # espera até o título do produto aparecer (ou outro elemento estável)
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-name')))
                except:
                    pass

                price = None

                # 1) JSON-LD
                if price is None:
                    try:
                        raw_ld = self.driver.find_element(By.CSS_SELECTOR, 'script[type="application/ld+json"]').get_attribute('innerHTML')
                        data_ld = json.loads(raw_ld)
                        # pode ser lista ou dicionário
                        if isinstance(data_ld, list):
                            for entry in data_ld:
                                if entry.get('@type') == 'Product' and 'offers' in entry:
                                    price = float(entry['offers'].get('price') or 0)
                                    break
                        elif data_ld.get('@type') == 'Product' and 'offers' in data_ld:
                            price = float(data_ld['offers'].get('price') or 0)
                    except:
                        pass

                # 2) meta[itemprop="price"]
                if price is None:
                    try:
                        price_elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[itemprop="price"]')))
                        raw_price = price_elem.get_attribute('content')
                        if raw_price:
                            price = float(raw_price)
                    except:
                        price = None

                # 3) seletor visual
                if price is None:
                    try:
                        elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.skuBestPrice, .product-price, .price, [data-price]')))
                        if elem.is_displayed():
                            # primeiro tente “data-price”
                            raw_data = elem.get_attribute('data-price') or ''
                            if raw_data:
                                price = float(raw_data)
                            else:
                                text = elem.text or ''
                                if text.strip():
                                    price_text = text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                                    price = float(price_text)
                    except:
                        price = None

                yield {
                    'produto_id': pid,
                    'preco_raia': price,
                    'url_raia': url
                }

            except Exception as e:
                self.logger.error(f"Erro ao processar {url}: {e}")
                yield {
                    'produto_id': pid,
                    'preco_raia': None,
                    'url_raia': url
                }
