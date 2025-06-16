import json
import os
import pandas as pd

class ExcelPipeline:
    def open_spider(self, spider):
        # Tenta carregar progresso anterior
        if os.path.exists('progress.json'):
            with open('progress.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            spider.logger.info(f"Pipeline carregou progresso de {len(self.data)} produtos")
        else:
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            self.data = {
                str(p['id']): {  # Convertendo ID para string para garantir consistência
                    'Id do produto':       p['id'],
                    'nome':                p['name'],
                    'preco_amazon':        None,
                    'url_amazon':          '',
                    'preco_epoca':         None,
                    'url_epoca':           '',
                    'preco_mercadolivre':  None,
                    'url_mercadolivre':    '',
                    'preco_pacheco':       None,
                    'url_pacheco':         '',
                    'preco_raia':          None,
                    'url_raia':            ''
                }
                for p in products
            }
            spider.logger.info(f"Pipeline inicializado com {len(self.data)} produtos")

    def process_item(self, item, spider):
        pid = str(item.get('produto_id'))  # Convertendo ID para string
        if pid in self.data:
            rec = self.data[pid]
            for k, v in item.items():
                if k.startswith('preco_') or k.startswith('url_'):
                    # Só atualiza se o valor não for None e o campo atual estiver vazio
                    if v is not None and (rec[k] is None or rec[k] == ''):
                        rec[k] = v
            spider.logger.info(f"Processado item para produto {pid}: {item}")
        else:
            spider.logger.warning(f"Produto ID {pid} não encontrado no dicionário de dados")
        return item

    def close_spider(self, spider):
        # Salva os dados em JSON para debug
        with open(f'debug_{spider.name}.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        spider.logger.info(f"Dados salvos em debug_{spider.name}.json")

        # Salva progresso acumulado
        with open('progress.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        spider.logger.info("Progresso salvo em progress.json")

        # Só gera o Excel quando a última spider (EpocaSpider) fechar
        if spider.name != 'epoca':
            spider.logger.info(f"Spider {spider.name} finalizada, aguardando EpocaSpider")
            return

        spider.logger.info("Gerando relatório Excel...")
        excel_file = 'precos_report.xlsx'
        if os.path.exists(excel_file):
            os.remove(excel_file)

        df = pd.DataFrame(self.data.values())
        lojas = ['amazon', 'epoca', 'mercadolivre', 'pacheco', 'raia']
        
        # Log dos dados antes de calcular a média
        for loja in lojas:
            preco_col = f'preco_{loja}'
            spider.logger.info(f"Preços da {loja}: {df[preco_col].tolist()}")
        
        # Calcula a média apenas com os preços disponíveis
        df['média'] = df[[f'preco_{l}' for l in lojas]].mean(axis=1)
        
        for l in lojas:
            preco_col = f'preco_{l}'
            url_col   = f'url_{l}'
            def make_link(row):
                val = row[preco_col]
                url = row[url_col]
                if pd.notna(val) and url:
                    return f'=HYPERLINK("{url}", "{val:.2f}")'
                return 'indisp.'
            df[preco_col] = df.apply(make_link, axis=1)

        df = df.rename(columns={f'preco_{l}': f'valor_{l}' for l in lojas})
        cols = ['Id do produto', 'nome'] + [f'valor_{l}' for l in lojas] + ['média']
        df = df[cols]

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Preços')
        spider.logger.info(f"Arquivo {excel_file} gerado com sucesso.")
        # Remove progresso ao final
        if os.path.exists('progress.json'):
            os.remove('progress.json')

