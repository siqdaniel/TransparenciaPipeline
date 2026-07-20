 Aluno: Daniel Victor Sampaio Siqueira
 Turma: Analise de Dados com Python V2
 
 
 Pipeline de Dados e Transparência de Gastos Públicos com Viagens a Serviço (Arquitetura Medallion)
 1. Problema de Negócio
Os dados abertos sobre despesas e viagens a serviço do Governo Federal são disponibilizados de forma bruta no Portal da Transparência. Devido ao grande volume de dados desorganizados, problemas de tipagem, duplicidades e ausência de padronização, a tomada de decisão rápida e a auditoria dos gastos públicos tornam-se desafios complexos.

Objetivo do Projeto:
Construir um pipeline ETL (Extract, Transform, Load) robusto e automatizado que consuma os dados brutos oficiais, estruture a informação em camadas lógicas (Arquitetura Medallion) e responda a perguntas essenciais de gestão com métricas e visualizações legíveis e confiáveis.

 2. Tecnologias e Arquitetura

Stack de Tecnologias
Linguagem: Python

Banco de Dados Relacional: MySQL

Manipulação e Carga de Dados: pandas, mysql-connector-python / psycopg2

Visualização de Dados (Dataviz): matplotlib, seaborn

Orquestração e Versionamento: Git e GitHub



 Arquitetura Proposta (Medallion Architecture)
 [ Portal da Transparência (.zip) ]
                 │
                 ▼ (1_extrair.py)
 ┌───────────────────────────────────────────────┐
 │               CAMADA RAW                      │ 
 │  (Cópia fiel do dado bruto em VARCHAR)       │
 └──────────────────────┬────────────────────────┘
                        │
                        ▼ (2_transformar.py)
 ┌───────────────────────────────────────────────┐
 │               CAMADA SILVER                   │
 │  (Dado limpo, tipado, PK, FK e Constraints)   │
 └──────────────────────┬────────────────────────┘
                        │
                        ▼ (3_analise.ipynb)
 ┌───────────────────────────────────────────────┐
 │               CAMADA GOLD                     │
 │  (Visões agregadas, métricas e Dataviz)       │
 └───────────────────────────────────────────────┘


Detalhamento das Camadas
Raw (Bronze): Preservação integral do histórico extraído. Carga idempotente (TRUNCATE prévio) armazenando todas as colunas no formato VARCHAR para auditoria.

Silver: Limpeza, tratamento de nulos/formatos, conversões explícitas para DECIMAL e DATE, e aplicação de integridade referencial com Chaves Primárias (PK), Chaves Estrangeiras (FK) e Restrições (NOT NULL, CHECK, UNIQUE).

Gold: Modelagem de tabelas agregadas (JOIN + GROUP BY), relatórios analíticos no Jupyter Notebook e gráficos interativos/estáticos.

3. Estrutura do Repositório
Plaintext
├── .env.example          # Modelo para configuração de variáveis de ambiente
├── .gitignore            # Arquivos ignorados (dados brutos, credenciais, etc.)
├── requirements.txt      # Dependências e bibliotecas do projeto
├── 0_criar_banco.sql     # DDL de criação das tabelas Raw e Silver com constraints
├── 1_extrair.py          # Script de extração (Download do ZIP e carga na Raw)
├── 2_transformar.py      # Script de transformação e carga na Silver
├── 3_analise.ipynb       # Notebook da Camada Gold (Análises, SQL e Dataviz)
└── README.md             # Documentação completa do projeto

 4. Como Executar o Projeto
Pré-requisitos
Python 3.10+ instalado.

Instância do MySQL Server em execução.

Ferramenta de controle de versão Git.

Passo a Passo
a. Clonar o Repositório:

git clone https://github.com/siqdaniel/TransparenciaPipeline
cd TransparenciaPipeline

b. Configurar o Ambiente Virtual:

python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

c. Instalar Dependências:

pip install -r requirements.txt

d. Configurar Variáveis de Ambiente:
Copie o arquivo .env.example para .env e ajuste suas credenciais de banco de dados e IDs de acesso:

cp .env.example .env

e. Criar a Estrutura do Banco de Dados:
Execute o script DDL 0_criar_banco.sql no seu SGBD (MySQL) para criar o banco de dados e as tabelas Raw e Silver.

f. Executar a Camada Raw (Extração):

python 1_extrair.py

g.Executar a Camada Silver (Transformação):

python 2_transformar.py


h. Executar a Camada Gold (Análise e Dataviz):

Abra o Jupyter Notebook 3_analise.ipynb e execute todas as células.



5. Principais Insights e Conclusões
Com base na análise efetuada na Camada Gold, os seguintes pontos chave foram identificados:

Órgãos com Maior Custo: Os órgãos vinculados à defesa e ao planejamento externo concentram os maiores volumes absolutos em passagens e diárias.

Destinos e Custo Médio: Viagens internacionais e trajetos específicos para polos regionais apresentam custos médios por viagem substancialmente mais elevados quando comparados às rotas frequentes do eixo Brasília-capitais.

Distribuição de Trechos e Transportes: O transporte aéreo domina a maior parte dos trechos cadastrados, influenciando diretamente o ticket médio das despesas públicas tratadas.
 6. Melhorias Futuras
Orquestração de Pipelines: Implementação de ferramentas como Apache Airflow ou Prefect para agendamento automático das etapas de extração e transformação.

Conteinerização: Criação de um docker-compose.yml para subir o banco de dados e o ambiente de execução em containers isolados.

Qualidade de Dados Avançada: Adição de suítes de teste de qualidade de dados com Great Expectations.

Dashboard Interativo: Construção de um painel interativo utilizando Streamlit ou Power BI consumindo diretamente as visões da Camada Gold.