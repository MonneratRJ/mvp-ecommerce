# Catálogo de Dados — MVP E-commerce Olist

## Visão Geral

Pipeline de dados estruturado em arquitetura Medalhão (Bronze → Silver → Gold) no Databricks
Free Edition, a partir do dataset público **Brazilian E-Commerce Public Dataset by Olist**
(Kaggle, dados reais anonimizados de ~100 mil pedidos entre 2016 e 2018).

Este catálogo documenta as tabelas de todas as camadas, mas com maior nível de detalhe na
camada Gold, que é a consumida diretamente pelas perguntas de negócio deste MVP:

1. **Frete vs. porte físico do produto** — quais categorias pagam mais frete por quilo/volume
   transportado?
2. **Concentração de problemas por vendedor** — um grupo pequeno de vendedores concentra a
   maior parte dos atrasos e notas baixas?

**Licença dos dados:** _Brazilian E-Commerce Public Dataset by Olist_ (Kaggle), licenciado sob
**CC BY-NC-SA 4.0** (uso não comercial, com atribuição e compartilhamento pelas mesmas regras).

**Nomenclatura das tabelas:** todas as tabelas vivem no catálogo `workspace`, qualificadas por
schema — `workspace.olist_bronze.<tabela>`, `workspace.olist_silver.<tabela>` e
`workspace.olist_gold.<tabela>`. Por brevidade, este catálogo referencia apenas `<schema>.<tabela>`
(ex.: `olist_bronze.orders`) nas tabelas abaixo.

---

## Camada Bronze (Raw)

Cópia fiel dos CSVs originais, sem nenhuma transformação. Objetivo: rastreabilidade — se algo
der errado adiante, sempre é possível voltar aqui e conferir o dado exatamente como chegou.

| Tabela                     | Origem (CSV)                       | Conteúdo                                                         | Linhagem                                                        |
| -------------------------- | ---------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------- |
| `olist_bronze.orders`      | `olist_orders_dataset.csv`         | Um registro por pedido: status, datas do ciclo de vida do pedido | Fonte: Olist/Kaggle                                             |
| `olist_bronze.customers`   | `olist_customers_dataset.csv`      | Um registro por cliente (por pedido): localização                | Fonte: Olist/Kaggle                                             |
| `olist_bronze.products`    | `olist_products_dataset.csv`       | Um registro por produto: categoria, peso, dimensões físicas      | Fonte: Olist/Kaggle                                             |
| `olist_bronze.order_items` | `olist_order_items_dataset.csv`    | Um registro por item de pedido: produto, vendedor, preço, frete  | Fonte: Olist/Kaggle                                             |
| `olist_bronze.payments`    | `olist_order_payments_dataset.csv` | Um registro por pagamento: forma, parcelas, valor                | Fonte: Olist/Kaggle                                             |
| `olist_bronze.reviews`     | `olist_order_reviews_dataset.csv`  | Um registro por avaliação: nota, comentário                      | Fonte: Olist/Kaggle                                             |
| `olist_bronze.sellers`     | `olist_sellers_dataset.csv`        | Um registro por vendedor: localização                            | Fonte: Olist/Kaggle                                             |
| `olist_bronze.geolocation` | `olist_geolocation_dataset.csv`    | CEP ↔ latitude/longitude                                         | Fonte: Olist/Kaggle (não utilizada pelas 2 perguntas deste MVP) |

Metadados de controle (recomendado adicionar, se ainda não existir): `_ingestion_date`
(timestamp da carga) e `_source_file` (nome do CSV de origem) em cada tabela Bronze.

---

## Camada Silver (Clean)

Aplicadas limpeza, tipagem e validações básicas de qualidade sobre a Bronze. Principais
transformações relevantes para as duas hipóteses deste MVP:

| Tabela                     | Transformações aplicadas                                                                                                                                                                                       | Linhagem                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `olist_silver.orders`      | Remoção de `order_id`/`customer_id` nulos; conversão de datas para timestamp; **`order_estimated_delivery_date` preservada e tipada** (necessária para calcular atraso real)                                   | De `olist_bronze.orders`      |
| `olist_silver.customers`   | Remoção de `customer_id` nulo                                                                                                                                                                                  | De `olist_bronze.customers`   |
| `olist_silver.products`    | Remoção de `product_id` nulo; peso/dimensões convertidos para `double`; **remoção de peso/dimensão <= 0** (fisicamente impossível); nulos em peso/dimensão mantidos (não são erro, são ausência de informação) | De `olist_bronze.products`    |
| `olist_silver.order_items` | Remoção de `order_id`/`product_id`/**`seller_id`** nulos (chave central da Pergunta 2)                                                                                                                         | De `olist_bronze.order_items` |
| `olist_silver.payments`    | Remoção de `order_id` nulo; `payment_installments`/`payment_value` tipados                                                                                                                                     | De `olist_bronze.payments`    |
| `olist_silver.reviews`     | Remoção de `order_id` nulo; `review_score` validado no domínio 1-5                                                                                                                                             | De `olist_bronze.reviews`     |
| `olist_silver.sellers`     | Remoção de `seller_id` nulo                                                                                                                                                                                    | De `olist_bronze.sellers`     |
| `olist_silver.geolocation` | Deduplicação por CEP                                                                                                                                                                                           | De `olist_bronze.geolocation` |

---

## Camada Gold (Analytics)

Modelo dimensional: **1 tabela fato** (`olist_gold.fato_vendas`) cercada de **4 dimensões**
(`olist_gold.dim_clientes`, `olist_gold.dim_produtos`, `olist_gold.dim_vendedores`,
`olist_gold.dim_avaliacoes`).

### ⭐ FATO_VENDAS (tabela principal)

Grão: uma linha por item de pedido (order_id + product_id + seller_id), com informações
consolidadas de pagamento e avaliação do pedido.

| Campo                           | Descrição                                     | Tipo      | Domínio de valores                                                                                                                               | Linhagem                                                            |
| ------------------------------- | --------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `order_id`                      | Identificador do pedido                       | string    | —                                                                                                                                                | `olist_silver.orders.order_id`                                      |
| `customer_id`                   | Cliente que fez o pedido                      | string    | Link → `dim_clientes`                                                                                                                            | `olist_silver.orders.customer_id`                                   |
| `product_id`                    | Produto do item                               | string    | Link → `dim_produtos`                                                                                                                            | `olist_silver.order_items.product_id`                               |
| `seller_id`                     | Vendedor que cumpriu o item                   | string    | Link → `dim_vendedores`                                                                                                                          | `olist_silver.order_items.seller_id`                                |
| `review_id`                     | Avaliação associada ao pedido                 | string    | Pode ser nulo (pedido sem review)                                                                                                                | `olist_silver.reviews.review_id`                                    |
| `review_score`                  | Nota dada pelo cliente                        | int       | 1 a 5, ou nulo                                                                                                                                   | `olist_silver.reviews.review_score`                                 |
| `payment_type`                  | Forma de pagamento                            | string    | `credit_card`, `boleto`, `voucher`, `debit_card`, etc.                                                                                           | `olist_silver.payments.payment_type`                                |
| `payment_installments`          | Número de parcelas                            | int       | ≥ 1                                                                                                                                              | `olist_silver.payments.payment_installments`                        |
| `payment_value`                 | Valor total pago                              | double    | ≥ 0 (BRL)                                                                                                                                        | `olist_silver.payments.payment_value`                               |
| `price`                         | Preço do item (produto)                       | double    | ≥ 0 (BRL)                                                                                                                                        | `olist_silver.order_items.price`                                    |
| `freight_value`                 | Valor do frete do item                        | double    | ≥ 0 (BRL)                                                                                                                                        | `olist_silver.order_items.freight_value`                            |
| `order_date`                    | Data/hora da compra                           | timestamp | —                                                                                                                                                | `olist_silver.orders.order_purchase_timestamp`                      |
| `delivery_date`                 | Data/hora da entrega ao cliente               | timestamp | Nulo se ainda não entregue                                                                                                                       | `olist_silver.orders.order_delivered_customer_date`                 |
| `order_estimated_delivery_date` | Data estimada de entrega prometida ao cliente | timestamp | —                                                                                                                                                | `olist_silver.orders.order_estimated_delivery_date`                 |
| `delivery_days`                 | Dias corridos entre compra e entrega          | int       | ≥ 0, nulo se não entregue                                                                                                                        | Calculado: `DATEDIFF(delivery_date, order_date)`                    |
| `dias_vs_estimativa`            | Diferença entre entrega real e estimada       | int       | Negativo = adiantado; positivo = atrasado; nulo se não entregue                                                                                  | Calculado: `DATEDIFF(delivery_date, order_estimated_delivery_date)` |
| `delivery_status`               | Categoria de pontualidade da entrega          | string    | `adiantado_ou_no_prazo` (dias_vs_estimativa ≤ 0) · `atraso_1_7_dias` (1–7) · `atraso_mais_de_7_dias` (> 7) · `nao_entregue` (delivery_date nulo) | Calculado a partir de `dias_vs_estimativa`                          |

**Por que `delivery_status` compara com a estimativa, e não usa só `delivery_days`:** um pedido
pode levar 15 dias e estar no prazo, se a estimativa era de 20. Medir contra a promessa feita ao
cliente é o que torna a Pergunta 2 (concentração de atrasos por vendedor) tecnicamente correta —
comparar vendedores por dias corridos penalizaria injustamente quem entrega em regiões
naturalmente mais distantes.

---

### DIM_PRODUTOS

Grão: um produto (`product_id`). Enriquecida com os campos físicos necessários para a
Pergunta 1.

| Campo                   | Descrição                                          | Tipo   | Domínio de valores                         | Linhagem                                      |
| ----------------------- | -------------------------------------------------- | ------ | ------------------------------------------ | --------------------------------------------- |
| `product_id`            | Identificador do produto                           | string | Chave primária                             | `olist_silver.products.product_id`            |
| `product_category_name` | Categoria do produto (nome original, em português) | string | ~70 categorias distintas                   | `olist_silver.products.product_category_name` |
| `product_weight_g`      | Peso do produto em gramas                          | double | > 0, ou nulo (produto sem essa informação) | `olist_silver.products.product_weight_g`      |
| `product_length_cm`     | Comprimento em cm                                  | double | > 0, ou nulo                               | `olist_silver.products.product_length_cm`     |
| `product_height_cm`     | Altura em cm                                       | double | > 0, ou nulo                               | `olist_silver.products.product_height_cm`     |
| `product_width_cm`      | Largura em cm                                      | double | > 0, ou nulo                               | `olist_silver.products.product_width_cm`      |

**Nota de qualidade:** produtos com peso/dimensão nula foram mantidos na tabela (o produto em
si é válido), mas são **explicitamente excluídos** na query da Pergunta 1 via `WHERE ... IS NOT
NULL` — decisão documentada no notebook de análise, não um filtro silencioso.

---

### DIM_VENDEDORES

Grão: um vendedor (`seller_id`). Usada como dimensão central da Pergunta 2.

| Campo       | Descrição                 | Tipo   | Domínio de valores | Linhagem                            |
| ----------- | ------------------------- | ------ | ------------------ | ----------------------------------- |
| `seller_id` | Identificador do vendedor | string | Chave primária     | `olist_silver.sellers.seller_id`    |
| `state`     | Estado (UF) do vendedor   | string | 27 UFs do Brasil   | `olist_silver.sellers.seller_state` |
| `city`      | Cidade do vendedor        | string | —                  | `olist_silver.sellers.seller_city`  |

---

### DIM_CLIENTES

Grão: um cliente/pedido (`customer_id` — cada pedido gera um `customer_id` próprio no dataset
original; não é o identificador único da pessoa).

| Campo         | Descrição                                 | Tipo       | Domínio de valores | Linhagem                                          |
| ------------- | ----------------------------------------- | ---------- | ------------------ | ------------------------------------------------- |
| `customer_id` | Identificador do cliente para este pedido | string     | Chave primária     | `olist_silver.customers.customer_id`              |
| `state`       | Estado (UF) do cliente                    | string     | 27 UFs do Brasil   | `olist_silver.customers.customer_state`           |
| `city`        | Cidade do cliente                         | string     | —                  | `olist_silver.customers.customer_city`            |
| `zip_code`    | Prefixo do CEP do cliente                 | string/int | 5 dígitos          | `olist_silver.customers.customer_zip_code_prefix` |

---

### DIM_AVALIACOES

Grão: uma nota possível (tabela de apoio/lookup, não transacional).

| Campo          | Descrição              | Tipo   | Domínio de valores                                           | Linhagem                                 |
| -------------- | ---------------------- | ------ | ------------------------------------------------------------ | ---------------------------------------- |
| `rating`       | Nota numérica          | int    | 1 a 5                                                        | `olist_silver.reviews.review_score`      |
| `rating_label` | Rótulo textual da nota | string | `Excelente` (5) · `Bom` (4) · `Aceitável` (3) · `Ruim` (≤ 2) | Derivado via `CASE` a partir de `rating` |

---

## Resumo de Qualidade de Dados (camada Gold)

| Dimensão de qualidade | O que foi verificado                                                                                                                                      | Tratamento                                                                                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Completude**        | Nulos em chaves primárias/estrangeiras (`order_id`, `customer_id`, `product_id`, `seller_id`)                                                             | Registros sem essas chaves foram removidos ainda na Silver                                                                                                               |
| **Completude**        | Nulos em `product_weight_g`/dimensões                                                                                                                     | Mantidos na Silver/Gold; excluídos explicitamente na análise da Pergunta 1                                                                                               |
| **Acurácia**          | Peso/dimensão de produto ≤ 0                                                                                                                              | Removidos na Silver (fisicamente impossível, provável erro de cadastro)                                                                                                  |
| **Consistência**      | Datas em formatos variados                                                                                                                                | Convertidas para `timestamp` único na Silver                                                                                                                             |
| **Consistência**      | `delivery_status` calculado de forma homogênea (via `dias_vs_estimativa`), evitando ambiguidade entre "demorou muito" e "atrasou em relação ao prometido" | Coluna derivada, documentada nesta tabela                                                                                                                                |
| **Unicidade**         | Duplicatas de `order_id` em `olist_bronze.orders`                                                                                                         | Verificadas via `dropDuplicates`; nenhuma removida além de checagem (dataset já vem sem duplicatas relevantes)                                                           |
| **Outliers**          | Amostras pequenas por categoria/vendedor podem distorcer médias                                                                                           | Filtro `HAVING COUNT(*) >= 30` (categorias) e `>= 10` (vendedores) aplicado nas queries de análise, para excluir grupos com volume insuficiente para conclusão confiável |
