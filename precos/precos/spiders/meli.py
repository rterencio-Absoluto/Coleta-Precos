import scrapy
import json

class MeliSpider(scrapy.Spider):
    name = "meli"
    allowed_domains = ["mercadolivre.com.br"]

    def start_requests(self):
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        for prod in products:
            pid = prod['id']
            ml_id = prod.get('ml_id')
            if not ml_id:
                continue
            url = f"https://www.mercadolivre.com.br/p/{ml_id}"
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'produto_id': pid},
                dont_filter=True
            )

    def parse(self, response):
        pid = response.meta['produto_id']

        # extrai o preço diretamente do <meta itemprop="price" content="...">
        price_meta = response.css('meta[itemprop="price"]::attr(content)').get()
        try:
            price = float(price_meta) if price_meta else None
        except ValueError:
            price = None

        yield {
            'produto_id':         pid,
            'preco_mercadolivre': price,
            'url_mercadolivre':   response.url
        }
