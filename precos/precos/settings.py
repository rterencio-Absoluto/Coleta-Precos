# settings.py do seu projeto Scrapy

BOT_NAME = 'precos'

SPIDER_MODULES = ['precos.spiders']
NEWSPIDER_MODULE = 'precos.spiders'

# Respeitar robots.txt
ROBOTSTXT_OBEY = False

# Habilita cookies (muitas vezes útil para sites VTEX)
COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;'
              'q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Referer': 'https://www.drogaraia.com.br/'
}


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)


# Exportar feeds (JSON/CSV) em UTF-8
FEED_EXPORT_ENCODING = 'utf-8'

# ativa nosso pipeline de ordenação
ITEM_PIPELINES = {
    'precos.pipelines.ExcelPipeline': 300,
}


# garante UTF-8 na exportação
FEED_EXPORT_ENCODING = 'utf-8'

# (Opcional para evitar bans)
# DOWNLOAD_DELAY = 1
# CONCURRENT_REQUESTS = 8
# USER_AGENT = 'Mozilla/5.0 (compatible; PreçosBot/1.0; +http://seusite.com)'
