import scrapy
import json
from precos.items import ProductItem

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.com.br"]

    def start_requests(self):
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        for prod in products:
            produto_id = prod['id']
            asin = prod.get('asin')
            if not asin:
                continue
            url = f"https://www.amazon.com.br/dp/{asin}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'produto_id': produto_id},
                dont_filter=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )

    def parse(self, response):
        produto_id = response.meta['produto_id']
        preco = None

        # Tenta diferentes seletores CSS para o preço
        selectors = [
            # Seletor padrão
            ('.a-price-whole::text', '.a-price-fraction::text'),
            # Seletor alternativo
            ('.a-price .a-offscreen::text', None),
            # Seletor para produtos em oferta
            ('.a-price .a-offscreen::text', None),
            # Seletor para produtos com desconto
            ('.a-price .a-offscreen::text', None)
        ]

        for whole_selector, frac_selector in selectors:
            try:
                if frac_selector:
                    whole = response.css(whole_selector).get(default='').replace('.', '')
                    frac = response.css(frac_selector).get(default='')
                    if whole and frac:
                        preco = float(f"{whole}.{frac}")
                else:
                    # Para seletores que retornam o preço completo
                    preco_text = response.css(whole_selector).get(default='')
                    if preco_text:
                        # Remove R$ e converte vírgula para ponto
                        preco_text = preco_text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        preco = float(preco_text)
                
                if preco is not None:
                    break
            except (ValueError, AttributeError):
                continue

        yield {
            'produto_id': produto_id,
            'preco_amazon': preco,
            'url_amazon': response.url,
            'status': 'sucesso' if preco is not None else 'erro'
        }
