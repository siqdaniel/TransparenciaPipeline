# 📊 ETL & Analytics: Transparência de Gastos Públicos com Viagens

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/MySQL-8.0%2B-orange?style=for-the-badge&logo=mysql" />
  <img src="https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas" />
  <img src="https://img.shields.io/badge/Seaborn-Dataviz-3776AB?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Architecture-Medallion-green?style=for-the-badge" />
</p>

---

## 📌 1. Escopo & Problema de Negócio

Os dados abertos de viagens e diárias do Governo Federal (Portal da Transparência) contêm um grande volume de registros brutos, inconsistências de tipagem e duplicidades, o que dificulta a auditoria rápida dos recursos públicos.

**Objetivo:** Construir um pipeline de dados automatizado sob a **Arquitetura Medallion** (Raw ➔ Silver ➔ Gold) para tratar esses dados e fornecer **respostas analíticas claras e fundamentadas** para a gestão pública.

---

## 🏛️ 2. Arquitetura da Solução

```text
 ┌─────────────────────────────────────────────────────────┐
 │                      CAMADA RAW                         │
 │  - Ingestão dos CSVs brutos do Portal da Transparência │
 │  - Persistência idempotente em formato VARCHAR          │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼ (src/2_transformar.py)
 ┌─────────────────────────────────────────────────────────┐
 │                     CAMADA SILVER                       │
 │  - Limpeza de strings e sanitização de caracteres      │
 │  - Conversão de tipos (DATE, DECIMAL)                   │
 │  - Aplicação de regras de integridade (PK, FK)          │
 └────────────────────────────┬────────────────────────────┘
                              │
                              ▼ (notebooks/3_analise.ipynb)
 ┌─────────────────────────────────────────────────────────┐
 │                      CAMADA GOLD                        │
 │  - Agregações analíticas via SQL                        │
 │  - Dataviz e relatórios das perguntas de negócio        │
 └─────────────────────────────────────────────────────────┘
--
📂3. Organização do Repositório

```text
ProjetoFinalV2/
├── sql/
│   └── 0_criar_banco.sql    # DDLs de criação do banco e tabelas (Raw/Silver)
├── src/
│   ├── config.py            # Credenciais e variáveis de ambiente
│   ├── banco.py             # Funções de conexão e execução SQL
│   ├── 1_extrair.py         # Pipeline de extração para a Camada Raw
│   └── 2_transformar.py     # Pipeline de transformação para a Camada Silver
├── notebooks/
│   └── 3_analise.ipynb      # Notebook analítico da Camada Gold (Dataviz)
├── requirements.txt         # Bibliotecas e dependências do projeto
└── README.md                # Documentação oficial do projeto