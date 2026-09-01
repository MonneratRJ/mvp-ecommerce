# Catálogo de dados

Os objetos estão em `<catalogo>.olist_gold`; todos são tabelas Delta produzidas pelo
notebook `02_gold_star_schema.sql`. A origem é o CSV de mesmo tema em
`/Volumes/<catalogo>/olist_bronze/raw`, transformado pela tabela Silver indicada.

## `dim_clientes`

Origem: `olist_customers_dataset.csv` → `silver.customers`.

| Coluna | Tipo | Descrição / domínio |
| --- | --- | --- |
| `customer_id` | STRING | chave da dimensão; não nula |
| `customer_city` | STRING | cidade do cliente |
| `customer_state` | STRING | sigla UF brasileira |

## `dim_produtos`

Origem: `olist_products_dataset.csv` → `silver.products`.

| Coluna | Tipo | Descrição / domínio |
| --- | --- | --- |
| `product_id` | STRING | chave da dimensão; não nula |
| `product_category_name` | STRING | categoria; `sem_categoria` quando ausente |

## `dim_avaliacoes`

Origem: domínio fixo de notas 1 a 5, validado contra
`olist_order_reviews_dataset.csv` → `olist_silver.reviews`.

| Coluna | Tipo | Descrição / domínio |
| --- | --- | --- |
| `review_score` | INT | chave e nota da avaliação; valores de 1 a 5 |
| `review_label` | STRING | rótulo legível da nota |

## `dim_tempo`

Origem: `olist_orders_dataset.csv` → `silver.orders`.

| Coluna | Tipo | Descrição / domínio |
| --- | --- | --- |
| `purchase_date` | DATE | chave; data da compra |
| `year` | INT | ano da compra |
| `month` | INT | mês, 1 a 12 |
| `day` | INT | dia, 1 a 31 |
| `year_month` | STRING | período `yyyy-MM` |

## `fato_vendas`

Origem: pedidos, itens, pagamentos, avaliações e produtos Bronze → respectivas
tabelas Silver. Granularidade: um `order_item_id` de um pedido.

| Coluna | Tipo | Descrição / domínio |
| --- | --- | --- |
| `order_id` | STRING | identificador do pedido |
| `order_item_id` | INT | identificador sequencial do item no pedido |
| `customer_id` | STRING | FK para `dim_clientes` |
| `product_id` | STRING | FK para `dim_produtos` |
| `review_score` | INT | FK opcional para `dim_avaliacoes`; 1 a 5 |
| `purchase_date` | DATE | FK para `dim_tempo` |
| `payment_type` | STRING | método predominante no pedido |
| `price` | DECIMAL(12,2) | preço do item, em BRL |
| `freight_value` | DECIMAL(12,2) | frete do item, em BRL |
| `delivery_days` | INT | dias entre compra e entrega ao cliente |
| `delivery_delay_days` | INT | dias de entrega menos dias estimados; positivo é atraso |
| `delivery_status` | STRING | `adiantado_ou_no_prazo`, `atraso_1_7_dias`, `atraso_mais_de_7_dias` ou `nao_entregue` |
