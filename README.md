# MVP-ecommerce

**Aluno:** Marcelo Monnerat Castello  
**Matrícula:** 4052026000091  
**Curso:** PUC Rio — Pós-Graduação em Ciência de Dados

# Contexto de Negócios e Perguntas (Etapa 2. e 4.1)

## 1. O Problema de Negócio

A Olist é uma plataforma que conecta pequenos lojistas de todo o Brasil a grandes canais de venda (e-commerces) [5]. Embora o volume de vendas esteja crescendo, a diretoria identificou reclamações constantes de clientes sobre prazos de entrega, e suspeita que o custo de frete cobrado nem sempre reflete o porte físico real dos produtos.

Este projeto estrutura um pipeline de dados na nuvem (Databricks, arquitetura Medalhão) para investigar dois pontos operacionais da cadeia logística da Olist: (1) se o custo de frete é proporcional ao porte físico do produto ou indica ineficiência logística/pricing por categoria, e (2) se os problemas de atraso e insatisfação estão concentrados em um grupo pequeno de vendedores ou distribuídos por toda a base, apoiando decisões de auditoria comercial e revisão de precificação de frete.

## 2. Fonte de Dados e Licenciamento

- **Origem dos dados:** Os dados brutos foram obtidos no repositório Kaggle através do conjunto de dados público _Brazilian E-Commerce Public Dataset by Olist_ [4]. O dataset contém informações reais de aproximadamente 100 mil pedidos realizados no Brasil entre 2016 e 2018 [4].
- **Licença de Uso:** Os dados são disponibilizados sob a licença **CC BY-NC-SA 4.0** (Uso não comercial, com atribuição e compartilhamento igual) [4].

## 3. Perguntas de Negócio a serem Respondidas

Com o pipeline estruturado, buscaremos responder às seguintes perguntas analíticas:

1.  **Os custos de frete estão adequados?** Quais categorias de produto pagam mais frete por quilo/volume transportado, e isso é proporcional ao porte físico do produto ou indica ineficiência logística/pricing?
2.  **Os vendedores têm respeitado os prazos de entrega?** Um grupo pequeno de vendedores concentra a maior parte dos atrasos e notas baixas (padrão 80/20), ou o problema está distribuído por todos?

## 4. Carga dos Dados (Etapa 4.2)

_[a preencher após execução no Databricks: como os 9 CSVs foram enviados ao Volume `mvp_ecommerce`, screenshot da estrutura do Volume, referência aos notebooks `notebooks/00_bronze_ingestion.ipynb` a `03_business_analysis.ipynb`]_

## 5. Modelagem e Catálogo de Dados (Etapa 4.3)

Modelo em Esquema Estrela: 1 tabela fato (`fato_vendas`) cercada de 4 dimensões (`dim_clientes`, `dim_produtos`, `dim_vendedores`, `dim_avaliacoes`). Catálogo de dados completo, com descrição de cada tabela/campo, domínio de valores e linhagem: [.copilot/catalogo_dados.md](./.copilot/catalogo_dados.md).

_[a preencher: screenshots do Unity Catalog/Data Explorer mostrando o schema `olist_gold` com as 5 tabelas]_

## 6. Pipeline de Dados (Etapa 4.4)

Pipeline organizado em 4 notebooks, um por camada/etapa, seguindo a arquitetura Medalhão:

1. [`notebooks/00_bronze_ingestion.ipynb`](./notebooks/00_bronze_ingestion.ipynb) — carrega os 8 CSVs do Volume como tabelas Delta em `olist_bronze`, sem transformação.
2. [`notebooks/01_silver_transform.ipynb`](./notebooks/01_silver_transform.ipynb) — limpeza, tipagem e métricas de qualidade, grava em `olist_silver`.
3. [`notebooks/02_gold_star_schema.ipynb`](./notebooks/02_gold_star_schema.ipynb) — modela a fato e as 4 dimensões em `olist_gold`.
4. [`notebooks/03_business_analysis.ipynb`](./notebooks/03_business_analysis.ipynb) — responde às 2 perguntas de negócio com SQL sobre a camada Gold.

_[a preencher: screenshots confirmando a persistência das tabelas em cada schema no Databricks]_

## 7. Qualidade de Dados (Etapa 4.5)

Ver seção "Resumo de Qualidade de Dados" em [.copilot/catalogo_dados.md](./.copilot/catalogo_dados.md), que documenta completude, consistência, unicidade, acurácia e outliers verificados em cada camada, e como cada problema foi tratado (ex.: produtos com peso/dimensão ≤ 0 removidos na Silver; nulos em peso/dimensão mantidos e excluídos explicitamente na análise).

## 8. Análise de Dados (Etapa 4.5)

- **Pergunta 1 (os custos de frete estão adequados?):** Não. O custo de frete é muito alto para produtos pequenos/leves quando comparado a produtos grandes/pesados. Categorias leves (`telefonia`, `fashion_esporte`, `fashion_underwear_e_moda_praia`) pagam entre R$ 53 e R$ 60 por kg, enquanto categorias de móveis pesados (`moveis_escritorio`, `moveis_quarto`, `moveis_sala`) pagam entre R$ 3,56 e R$ 4,41 por kg — até 17x menos. O frete absoluto cresce pouco entre essas pontas (~2,6x) frente ao peso (~43x), indicando uma tarifa mínima/fixa por envio que penaliza itens leves. Recomendação: verificar alternativas para baratear o custo de frete de produtos pequenos/leves.
- **Pergunta 2 (os vendedores têm respeitado os prazos de entrega?):** Cerca de 20% dos vendedores concentram quase 75% dos atrasos e 68,5% das notas baixas, enquanto os melhores 20% não registraram nenhum atraso. Recomendação: priorizar maior auditoria e um plano de ação comercial focado nesses piores vendedores (renegociação de SLA, revisão de transportadora, ou desligamento em casos extremos). Outra sugestão é oferecer premiações aos melhores vendedores, seja com maior visibilidade de seus produtos, um selo de qualidade, etc.

## 9. Autoavaliação

**Objetivos atingidos:** o pipeline completo (Bronze → Silver → Gold) foi construído e as duas
perguntas de negócio definidas na Etapa 2 foram respondidas com evidência quantitativa: (1) o
custo de frete não é proporcional ao porte físico do produto, penalizando categorias leves; e
(2) os atrasos e notas baixas estão fortemente concentrados em ~20% dos vendedores, confirmando
o padrão 80/20. Os objetivos de modelagem (Esquema Estrela), catálogo de dados e qualidade de
dados também foram cumpridos conforme documentado nas seções 5 e 7.

**Trabalhos futuros:** enriquecer o modelo com a tabela `geolocation` (calcular distância real
entre vendedor e cliente e correlacionar com o frete e o atraso); construir um modelo preditivo
de risco de atraso por vendedor/pedido; automatizar o pipeline com jobs agendados no Databricks
em vez de execução manual dos notebooks; criar um dashboard (Databricks SQL ou ferramenta de BI)
para monitoramento contínuo dos indicadores de frete e SLA por vendedor.
