import scrapy

class ProductItem(scrapy.Item):
    produto_id            = scrapy.Field()
    nome                  = scrapy.Field()
    preco_amazon          = scrapy.Field()
    url_amazon            = scrapy.Field()
    preco_epoca           = scrapy.Field()
    url_epoca             = scrapy.Field()
    preco_mercadolivre    = scrapy.Field()
    url_mercadolivre      = scrapy.Field()
    preco_pacheco         = scrapy.Field()
    url_pacheco           = scrapy.Field()
    preco_raia            = scrapy.Field()
    url_raia              = scrapy.Field()
