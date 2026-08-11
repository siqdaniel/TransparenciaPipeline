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
 ```

 ---

## 📂 3. Organização do Repositório

| Diretório / Arquivo | Descrição |
| :--- | :--- |
| **`sql/`** | DDLs e scripts de criação do banco de dados (`0_criar_banco.sql`) |
| **`src/`** | Código-fonte dos pipelines Python (`1_extrair.py`, `2_transformar.py`, `config.py`, `banco.py`) |
| **`notebooks/`** | Notebook da Camada Gold com visualizações e análises (`3_analise.ipynb`) |
| **`requirements.txt`** | Dependências e bibliotecas do projeto Python |
| **`README.md`** | Documentação oficial do projeto |

---

---

## 📈 4. Análise de Negócio & Insights (Camada Gold)

### ❓ Pergunta 1: Quais os órgãos com maior volume de gastos em viagens?
* **Análise:** Os ministérios e órgãos vinculados à Defesa, Segurança Pública e Relações Exteriores concentram os maiores volumes orçamentários acumulados em passagens e diárias.
* **Insight:** O orçamento elevado justifica-se pelo caráter operacional contínuo dessas pastas, que demandam patrulhamento constante, ações de campo e missões diplomáticas no exterior.

### ❓ Pergunta 2: Quais os 3 destinos com maior custo médio por viagem?
* **Análise:** Agrupando os trechos por destino individual (`destino_cidade`), identificou-se que voos internacionais e destinos na Região Norte de difícil acesso logístico ocupam os primeiros lugares em custo médio.
* **Insight:** O custo é impactado pela combinação entre tarifas aéreas elevadas em rotas isoladas e a maior duração do deslocamento, aumentando a quantidade de diárias pagas aos servidores.

### ❓ Pergunta 3: Qual a distribuição dos meios de transporte utilizados?
* **Análise:** O modal **Aéreo** responde pela ampla maioria dos trechos registrados, superando expressivamente os modais **Rodoviário** e **Fluvial**.
* **Insight:** Apesar de garantir agilidade para viagens interfluviais e interestaduais, o transporte aéreo é o principal gargalo orçamentário. Políticas de compra e reserva antecipada podem gerar redução significativa nos custos.

---

---

## 💡 6. Melhorias Futuras

* **Orquestração de Pipelines:** Integração com **Apache Airflow** ou **Prefect** para automatizar o agendamento e o monitoramento diário das etapas do ETL.
* **Containerização:** Criação de um ambiente isolado e reprodutível com **Docker Compose**, simplificando a subida do banco MySQL e dos containers da aplicação.
* **Qualidade de Dados (Data Quality):** Implementação de suítes de testes automatizados com **Great Expectations** na Camada Silver para validar schema, valores nulos e duplicidades antes da carga Gold.
* **Dashboard Interativo:** Construção de um painel dinâmico em **Power BI** ou **Streamlit** para consumo visual das métricas de gastos diretamente por gestores públicos.


 