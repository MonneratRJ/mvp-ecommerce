# MVP — E-commerce da Olist

Pipeline Lakehouse para investigar a relação entre entrega, satisfação e pagamentos
no e-commerce da Olist, usando Databricks Free Edition e o padrão Medalhão.

## Contexto de Negócios e Perguntas (Etapa 2. e 4.1)

A Olist conecta pequenos lojistas brasileiros a marketplaces. Apesar do crescimento
das vendas, clientes relatam problemas de prazo de entrega e pagamento. Este projeto
organiza dados operacionais em uma camada analítica para responder:

1. Qual é o impacto do atraso na entrega na nota de avaliação do cliente (1 a 5)?
2. Quais estados possuem maior volume de vendas e qual método de pagamento predomina
   em cada um?

### Fonte, período e licença

* **Fonte:** [Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* **Período:** pedidos realizados entre 2016 e 2018; cerca de 100 mil pedidos
  anonimizados.
* **Licença:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/):
  uso não comercial, atribuição à Olist/Kaggle e compartilhamento pela mesma licença.

## Carga dos Dados (Etapa 4.2)

Baixe o dataset no Kaggle e envie, **sem alterações**, os CSVs abaixo para o Volume
`/Volumes/<catalogo>/olist_bronze/raw/`. A camada Bronze é o cofre de evidências:
não há limpeza, renomeação ou sobrescrita dos arquivos de origem.

| Arquivo | Uso |
| --- | --- |
| `olist_orders_dataset.csv` | datas e status do pedido |
| `olist_customers_dataset.csv` | cliente, cidade e estado |
| `olist_order_items_dataset.csv` | produto, preço e frete |
| `olist_order_payments_dataset.csv` | forma e valor de pagamento |
| `olist_order_reviews_dataset.csv` | avaliação do cliente |
| `olist_products_dataset.csv` | categoria do produto |

Execute `notebooks/00_bronze_ingestion.py` no Databricks, ajustando `CATALOG` se
necessário. O notebook cria o schema/Volume (quando permitido) e registra o
inventário dos arquivos em `olist_bronze.bronze_file_inventory`; os CSVs continuam
sendo a fonte imutável da Bronze.

> **Evidência a incluir na entrega:** captura do Unity Catalog exibindo o Volume
> `olist_bronze.raw` e os arquivos CSV enviados.

## Transformação e Qualidade dos Dados (Etapa 4.3)

`notebooks/01_silver_transform.py` lê os CSVs Bronze, converte tipos e grava tabelas
Delta no schema `olist_silver`. Registros inválidos não são silenciosamente
corrigidos: o notebook grava métricas de qualidade em
`olist_silver.data_quality_metrics`, permitindo auditoria antes de remover chaves
obrigatórias ou duplicidades.

| Dimensão | Regra aplicada | Tratamento |
| --- | --- | --- |
| Completude | `order_id`, `customer_id`, `product_id` e `review_score` são essenciais; mede nulos | descarta linhas sem chave; pedidos sem review permanecem sem avaliação |
| Consistência | datas são convertidas com `to_timestamp`; entrega não pode anteceder compra | datas inválidas viram `NULL`; durações impossíveis são excluídas do fato |
| Unicidade | deduplicação por chaves naturais de pedidos, clientes e produtos | mantém o primeiro registro determinístico |
| Acurácia | mede entregas acima de 500 dias e prazo negativo | não apaga o dado Bronze; sinaliza na métrica para investigação |
| Outliers | mede frete acima do percentil 99 | mantém o valor, evitando alterar receita sem decisão de negócio |

As tabelas Silver são Delta e podem ser reexecutadas com `overwrite`, preservando a
Bronze. A categoria é normalizada para `sem_categoria` quando ausente; isso evita
perder vendas por atributo descritivo incompleto.

## Modelagem dos Dados (Etapa 4.4)

`notebooks/02_gold_star_schema.sql` materializa o schema `gold` em estrela. A
granularidade de `fato_vendas` é **um item de pedido**. Assim, preço e frete não são
duplicados por joins de pagamento ou avaliação.

```text
dim_clientes ─┐
dim_produtos ─┼── fato_vendas ── dim_avaliacoes
dim_tempo ────┘
```

| Tabela | Chave | Finalidade |
| --- | --- | --- |
| `gold.dim_clientes` | `customer_id` | cidade e estado do cliente |
| `gold.dim_produtos` | `product_id` | categoria do produto |
| `gold.dim_avaliacoes` | `review_score` | domínio de notas de 1 a 5 |
| `gold.dim_tempo` | `purchase_date` | atributos de calendário da compra |
| `gold.fato_vendas` | `order_id`, `order_item_id` | métricas de preço, frete, entrega e atraso |

O catálogo completo — tipos, domínios e linhagem Bronze → Silver → Gold — está em
[`docs/catalogo_dados.md`](docs/catalogo_dados.md).

> **Evidência a incluir na entrega:** captura do Unity Catalog com as cinco tabelas
> `gold` gravadas em Delta.

## Pipeline de ETL (Etapa 4.5)

Os notebooks são separados por responsabilidade e devem ser executados nesta ordem:

1. `00_bronze_ingestion.py` — prepara a área imutável e inventaria os arquivos.
2. `01_silver_transform.py` — padroniza CSVs e registra qualidade.
3. `02_gold_star_schema.sql` — cria dimensões e fato.
4. `03_business_analysis.sql` — produz as respostas de negócio.

Todos aceitam o catálogo `workspace` como padrão. No Free Edition, importe os
arquivos pelo menu **Workspace → Import** e altere `CATALOG`/`${catalog}` caso seu
catálogo tenha outro nome.

## Análise Exploratória e Discussão (Etapa 4.6)

O notebook `03_business_analysis.sql` disponibiliza duas consultas reproduzíveis:

* segmenta pedidos entregues em `adiantado_ou_no_prazo`, `atraso_1_7_dias` e
  `atraso_mais_de_7_dias`, comparando pedidos, nota média e percentual de notas
  baixas (1–2);
* classifica estados por receita e pedidos e usa `ROW_NUMBER` para retornar a forma
  de pagamento dominante de cada estado, sem contar parcelas como pagamentos
  distintos.

Após executar, inclua aqui as capturas das tabelas/gráficos e uma discussão baseada
nos números observados. A conclusão não deve presumir causalidade: atraso e nota
baixa são associados nesta amostra e podem também refletir categoria, região ou
status do pedido.

| Evidência | Resultado após execução |
| --- | --- |
| Impacto do atraso na satisfação | _Adicionar captura e interpretação_ |
| Vendas e pagamento por estado | _Adicionar captura e interpretação_ |

## Autoavaliação (Etapa 5)

O modelo permite responder às duas perguntas: a primeira relaciona a classificação
de atraso à distribuição de `review_score`; a segunda agrega `fato_vendas` por
estado e elege a forma de pagamento por frequência de pedidos. A principal atenção
técnica é preservar a granularidade de item ao somar preço/frete e não multiplicar
valores ao relacionar pagamentos.

Como evolução de portfólio, este pipeline pode ser orquestrado por Airflow ou
Databricks Workflows, receber testes de qualidade com limites de alerta e alimentar
um dashboard com filtros de período, estado e categoria.
