import scrapy
import json

class EpocaSpider(scrapy.Spider):
    name = "epoca"
    # agora permitido apenas o domínio público “www.drogariaepoca.com.br”
    allowed_domains = ["www.drogariaepoca.com.br"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 5,
        # Se você usa o pipeline Excel, mantenha habilitado aqui:
        # 'ITEM_PIPELINES': {'precos.pipelines.ExcelPipeline': 300},
    }

    def start_requests(self):
        # lê o products.json que já contém “epoca_slug”
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for prod in products:
            pid = prod['id']
            slug = prod.get('epoca_slug')
            if not slug:
                continue

            # faz request para a URL pública (sem passar pelo VTEX interno)
            page_url = f"https://www.epocacosmeticos.com.br/{slug}/p"
            yield scrapy.Request(
                page_url,
                callback=self.parse_product,
                meta={'produto_id': pid, 'page_url': page_url},
                dont_filter=True
            )

    def parse_product(self, response):
        pid = response.meta['produto_id']
        page_url = response.meta['page_url']

        preco = None
        url_epoca = None

        # extrai o JSON Next.js que está dentro de <script id="__NEXT_DATA__">
        raw = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if not raw:
            self.logger.error(f"Não encontrou __NEXT_DATA__ no HTML (produto_id={pid})")
        else:
            try:
                data = json.loads(raw)

                # navega até os dados do produto:
                prod_content = (
                    data.get('props', {})
                        .get('pageProps', {})
                        .get('data', {})
                        .get('ProductContent', {})
                        .get('content', {})
                )

                # 1) preço: items[0].sellers[0].commertialOffer.Price
                items = prod_content.get('items', [])
                if items:
                    seller0 = items[0].get('sellers', [])[0]
                    comm = seller0.get('commertialOffer', {})
                    preco = comm.get('Price')

                # 2) link público: usa prod_content["linkText"]
                link_text = prod_content.get('linkText')
                if link_text:
                    url_epoca = f"https://www.epocacosmeticos.com.br/{link_text}/p"
                else:
                    url_epoca = page_url

            except Exception as e:
                self.logger.error(f"Erro ao desserializar JSON __NEXT_DATA__ (produto_id={pid}): {e}")

        yield {
            'produto_id': pid,
            'preco_epoca': preco,
            'url_epoca': url_epoca
        }
