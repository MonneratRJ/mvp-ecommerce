# MVP-ecommerce

**Aluno:** Marcelo Monnerat Castello  
**Matrícula:** 4052026000091  
**Curso:** PUC Rio — Pós-Graduação em Ciência de Dados

# Contexto de Negócios e Perguntas (Etapa 2. e 4.1)

## 1. O Problema de Negócio

A Olist é uma plataforma que conecta pequenos lojistas de todo o Brasil a grandes canais de venda (e-commerces) [5]. Embora o volume de vendas esteja crescendo, a diretoria identificou reclamações constantes de clientes sobre prazos de entrega e processamento de pagamentos [5].

Este projeto visa estruturar um pipeline de dados na nuvem utilizando o Databricks para analisar a logística de entregas e os meios de pagamento, auxiliando na tomada de decisões estratégicas para melhorar a experiência do cliente [4, 5].

## 2. Fonte de Dados e Licenciamento

- **Origem dos dados:** Os dados brutos foram obtidos no repositório Kaggle através do conjunto de dados público _Brazilian E-Commerce Public Dataset by Olist_ [4]. O dataset contém informações reais de aproximadamente 100 mil pedidos realizados no Brasil entre 2016 e 2018 [4].
- **Licença de Uso:** Os dados são disponibilizados sob a licença **CC BY-NC-SA 4.0** (Uso não comercial, com atribuição e compartilhamento igual) [4].

## 3. Perguntas de Negócio a serem Respondidas

Com o pipeline estruturado, buscaremos responder às seguintes perguntas analíticas:

1.  **Logística vs. Satisfação:** Qual o impacto do atraso na entrega na satisfação do cliente (nota de avaliação de 1 a 5)? [4]
2.  **Geografia vs. Pagamentos:** Quais estados brasileiros possuem o maior volume de vendas
