import subprocess
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_spider(spider_name):
    logger.info(f"Iniciando execução da spider: {spider_name}")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', spider_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info(f"Spider {spider_name} executada com sucesso")
            logger.debug(f"Output: {result.stdout}")
        else:
            logger.error(f"Erro ao executar spider {spider_name}")
            logger.error(f"Erro: {result.stderr}")
    except Exception as e:
        logger.error(f"Exceção ao executar spider {spider_name}: {str(e)}")
    
    logger.info(f"Aguardando 5 segundos antes da próxima spider...")
    time.sleep(5)  # Aumentando o tempo de espera entre as spiders

if __name__ == '__main__':
    spiders = ['amazon', 'meli', 'raia', 'pacheco', 'epoca']

    #spiders = ['amazon', 'meli', 'pacheco', 'epoca']
    
    
    logger.info("Iniciando execução sequencial das spiders")
    for spider in spiders:
        run_spider(spider)
    
    logger.info("Execução de todas as spiders concluída!") 