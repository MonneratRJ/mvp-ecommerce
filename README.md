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

1.  **Frete vs. porte físico do produto:** quais categorias de produto pagam mais frete por quilo/volume transportado, e isso é proporcional ao porte físico ou indica ineficiência logística/pricing?
2.  **Concentração de problemas em vendedores:** um grupo pequeno de vendedores concentra a maior parte dos atrasos e notas baixas (padrão 80/20), ou o problema está distribuído por todos?

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

- **Pergunta 1 (frete vs. porte físico):** _[preencher após rodar `03_business_analysis.ipynb` — categoria com pior `frete_medio_por_kg`, comparação com `volume_medio_m3`]_
- **Pergunta 2 (concentração por vendedor):** _[preencher — percentual de atrasos/notas baixas concentrado no decil 1 de vendedores]_

## 9. Autoavaliação

_[a preencher ao final: objetivos atingidos, dificuldades encontradas, trabalhos futuros]_
