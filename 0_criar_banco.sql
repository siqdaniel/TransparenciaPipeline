CREATE DATABASE IF NOT EXISTS transparenciaV2;
USE transparenciaV2;

-- ============================================================================
-- 1. DROP DAS TABELAS EXISTENTES (Garante Idempotência ao recomeçar)
-- ============================================================================
DROP TABLE IF EXISTS silver_trecho;
DROP TABLE IF EXISTS silver_passagem;
DROP TABLE IF EXISTS silver_pagamento;
DROP TABLE IF EXISTS silver_viagem;

DROP TABLE IF EXISTS raw_trecho;
DROP TABLE IF EXISTS raw_passagem;
DROP TABLE IF EXISTS raw_pagamento;
DROP TABLE IF EXISTS raw_viagem;

-- ============================================================================
-- 2. CAMADA RAW (Mapeamento idêntico aos layouts das imagens do CSV - Tudo TEXT)
-- ============================================================================

CREATE TABLE raw_viagem (
    identificador_do_processo_de_viagem TEXT,
    numero_da_proposta_pcdp TEXT,
    situacao TEXT,
    viagem_urgente TEXT,
    justificativa_urgencia_viagem TEXT,
    codigo_do_orgao_superior TEXT,
    nome_do_orgao_superior TEXT,
    codigo_orgao_solicitante TEXT,
    nome_orgao_solicitante TEXT,
    cpf_viajante TEXT,
    nome TEXT,
    cargo TEXT,
    funcao TEXT,
    descricao_funcao TEXT,
    periodo_data_de_inicio TEXT,
    periodo_data_de_fim TEXT,
    destinos TEXT,
    motivo TEXT,
    valor_diarias TEXT,
    valor_passagens TEXT,
    valor_devolucao TEXT,
    valor_outros_gastos TEXT
);

CREATE TABLE raw_passagem (
    identificador_do_processo_de_viagem TEXT,
    numero_da_proposta_pcdp TEXT,
    meio_transporte TEXT,
    pais_origem_ida TEXT,
    uf_origem_ida TEXT,
    cidade_origem_ida TEXT,
    pais_destino_ida TEXT,
    uf_destino_ida TEXT,
    cidade_destino_ida TEXT,
    pais_origem_volta TEXT,
    uf_origem_volta TEXT,
    cidade_origem_volta TEXT,
    pais_destino_volta TEXT,
    uf_destino_volta TEXT,
    cidade_destino_volta TEXT,
    valor_da_passagem TEXT,
    taxa_de_servico TEXT,
    data_da_emissao_compra TEXT,
    hora_da_emissao_compra TEXT
);

CREATE TABLE raw_pagamento (
    identificador_do_processo_de_viagem TEXT,
    numero_da_proposta_pcdp TEXT,
    codigo_do_orgao_superior TEXT,
    nome_do_orgao_superior TEXT,
    codigo_do_orgao_pagador TEXT,
    nome_do_orgao_pagador TEXT,
    codigo_da_unidade_gestora_pagadora TEXT,
    nome_da_unidade_gestora_pagadora TEXT,
    tipo_de_pagamento TEXT,
    valor TEXT
);

CREATE TABLE raw_trecho (
    identificador_do_processo_de_viagem TEXT,
    numero_da_proposta_pcdp TEXT,
    sequencia_trecho TEXT,
    origem_data TEXT,
    origem_pais TEXT,
    origem_uf TEXT,
    origem_cidade TEXT,
    destino_data TEXT,
    destino_pais TEXT,
    destino_uf TEXT,
    destino_cidade TEXT,
    meio_transporte TEXT,
    numero_diarias TEXT,
    missao TEXT
);

-- ============================================================================
-- 3. CAMADA SILVER (Dados Limpos, Tipados e com Chaves e Restrições Oficiais)
-- ============================================================================

CREATE TABLE silver_viagem (
    id_viagem VARCHAR(20) PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL, -- Constraint extra 1
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2), -- Calculado
    duracao_dias INT,          -- Calculado
    CONSTRAINT chk_valor_diarias CHECK (valor_diarias >= 0) -- Constraint extra 2
);

CREATE TABLE silver_passagem (
    id_passagem INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2),
    taxa_servico DECIMAL(10,2),
    data_emissao DATE,
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem),
    CONSTRAINT chk_val_passagem CHECK (valor_passagem >= 0), -- Constraint extra 1
    CONSTRAINT chk_taxa_servico CHECK (taxa_servico >= 0)    -- Constraint extra 2
);

CREATE TABLE silver_pagamento (
    id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL, -- Constraint extra 1
    valor DECIMAL(10,2),
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem),
    CONSTRAINT chk_valor_pagamento CHECK (valor >= 0) -- Constraint extra 2
);

CREATE TABLE silver_trecho (
    id_trecho INT AUTO_INCREMENT PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2),
    FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem),
    CONSTRAINT chk_num_diarias CHECK (numero_diarias >= 0), -- Constraint extra 1
    CONSTRAINT uq_viagem_trecho UNIQUE (id_viagem, sequencia_trecho) -- Constraint extra 2
);