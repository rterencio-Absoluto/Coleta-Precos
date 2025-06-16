import scrapy
import json
from urllib.parse import urlparse

class PachecoSpider(scrapy.Spider):
    name = "pacheco"
    allowed_domains = ["drogariaspacheco.vtexcommercestable.com.br", "www.drogariaspacheco.com.br"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 5,
        # Se quiser pipeline Excel, adicione aqui:
        # 'ITEM_PIPELINES': {'precos.pipelines.ExcelPipeline': 300},
    }

    def start_requests(self):
        # Leitura do JSON que contém "pacheco_sku"
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for prod in products:
            pid = prod['id']
            sku = prod.get('pacheco_sku')
            if not sku:
                continue

            # Endpoint JSON filtrando por skuId
            url = (
                "https://drogariaspacheco.vtexcommercestable.com.br/"
                f"api/catalog_system/pub/products/search?fq=skuId:{sku}"
            )

            yield scrapy.Request(
                url,
                callback=self.parse_price,
                meta={'produto_id': pid, 'sku': sku},
                dont_filter=True
            )

    def parse_price(self, response):
        pid = response.meta['produto_id']
        sku = response.meta['sku']
        price = None

        # URL fallback se nada for encontrado
        url_pacheco = f"https://www.drogariaspacheco.com.br/{sku}.html"

        try:
            data = response.json()

            if data and isinstance(data, list):
                produto = data[0]

                # 1) extrai o preço
                item0 = produto.get('items', [])[0]
                seller0 = item0.get('sellers', [])[0]
                offer = seller0.get('commertialOffer', {})
                price = offer.get('Price')

                # 2) extrai o campo 'link' (pode ser um URL completo ou apenas o path)
                link = produto.get('link') or produto.get('linkText')
                if link:
                    parsed = urlparse(link)
                    if parsed.netloc:  # é um URL completo
                        # usamos somente o caminho e prefixamos com www.drogariaspacheco.com.br
                        path = parsed.path
                        url_pacheco = f"https://www.drogariaspacheco.com.br{path}"
                        # caso tenha query ou parâmetros extras, você pode adicioná-los:
                        if parsed.query:
                            url_pacheco += f"?{parsed.query}"
                    else:
                        # link já é só o path (ex: "/algum-produto/p")
                        url_pacheco = f"https://www.drogariaspacheco.com.br{link}"
        except Exception as e:
            self.logger.error(f"Erro ao converter JSON para SKU {sku}: {e}")

        yield {
            'produto_id':    pid,
            'preco_pacheco': price,
            'url_pacheco':   url_pacheco
        }
