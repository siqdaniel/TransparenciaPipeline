"""
2_transformar.py
----------------
Lê os dados brutos das tabelas RAW, realiza o tratamento e limpeza das datas e valores,
calcula as colunas de métricas e povoa de forma segura as tabelas estruturadas da camada SILVER.
"""

from datetime import datetime
import mysql.connector
from banco import conectar, executar, inserir_em_lote
from config import TAMANHO_BLOCO

# --- Funções de Tratamento de Dados ---

def tratar_data(valor_texto):
    """Converte data 'DD/MM/AAAA' ou 'DD/MM/AAAA HH:MM:SS' para formato 'AAAA-MM-DD'."""
    if not valor_texto:
        return None
    valor_texto = valor_texto.strip()
    if not valor_texto or valor_texto.lower() in ("null", "none", ""):
        return None
    
    # Se contiver espaço (data e hora), pega apenas a parte da data
    if " " in valor_texto:
        valor_texto = valor_texto.split(" ")[0]
        
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(valor_texto, formato)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def tratar_decimal(valor_texto):
    """Converte valores numéricos em string brasileira para float (ex: '1.272,97' -> 1272.97)."""
    if not valor_texto:
        return 0.0
    valor_texto = valor_texto.strip()
    if not valor_texto or valor_texto.lower() in ("null", "none", ""):
        return 0.0
    try:
        # Remove pontos de milhar e substitui a vírgula decimal por ponto
        valor_limpo = valor_texto.replace(".", "").replace(",", ".")
        return float(valor_limpo)
    except ValueError:
        return 0.0


def calcular_duracao_dias(inicio, fim):
    """Calcula a diferença de dias entre duas datas formatadas (AAAA-MM-DD)."""
    if not inicio or not fim:
        return 0
    try:
        d1 = datetime.strptime(inicio, "%Y-%m-%d")
        d2 = datetime.strptime(fim, "%Y-%m-%d")
        return abs((d2 - d1).days)
    except Exception:
        return 0

# --- Processamento das Tabelas ---

def transformar_viagens(conexao):
    print(" Transformando dados para silver_viagem...")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 0;")
    executar(conexao, "TRUNCATE TABLE silver_viagem;")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 1;")

    cursor_raw = conexao.cursor(dictionary=True, buffered=True)
    cursor_raw.execute("SELECT * FROM raw_viagem;")
    
    lote = []
    sql_insert = """
        INSERT INTO silver_viagem (
            id_viagem, num_proposta, situacao, viagem_urgente, cod_orgao_superior,
            nome_orgao_superior, nome_viajante, cargo, data_inicio, data_fim,
            destinos, motivo, valor_diarias, valor_passagens, valor_devolucao,
            valor_outros_gastos, valor_total, duracao_dias
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    for linha in cursor_raw:
        # Conversão de valores e datas
        diarias = tratar_decimal(linha.get("valor_diarias"))
        passagens = tratar_decimal(linha.get("valor_passagens"))
        devolucao = tratar_decimal(linha.get("valor_devolucao"))
        outros = tratar_decimal(linha.get("valor_outros_gastos"))
        
        inicio = tratar_data(linha.get("periodo_data_de_inicio"))
        fim = tratar_data(linha.get("periodo_data_de_fim"))
        
        # Colunas Calculadas
        valor_total = (diarias + passagens + outros) - devolucao
        duracao = calcular_duracao_dias(inicio, fim)
        
        registro = (
            linha.get("identificador_do_processo_de_viagem"),
            linha.get("numero_da_proposta_pcdp"),
            linha.get("situacao"),
            linha.get("viagem_urgente"),
            linha.get("codigo_do_orgao_superior"),
            linha.get("nome_do_orgao_superior") or "ÓRGÃO NÃO INFORMADO",
            linha.get("nome"),
            linha.get("cargo"),
            inicio,
            fim,
            linha.get("destinos"),
            linha.get("motivo"),
            diarias,
            passagens,
            devolucao,
            outros,
            valor_total,
            duracao
        )
        lote.append(registro)
        
        if len(lote) >= TAMANHO_BLOCO:
            inserir_em_lote(conexao, sql_insert, lote)
            lote = []
            
    if lote:
        inserir_em_lote(conexao, sql_insert, lote)
    
    cursor_raw.close()
    print(" Carga de silver_viagem finalizada com sucesso!")


def transformar_passagens(conexao):
    print(" Transformando dados para silver_passagem...")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 0;")
    executar(conexao, "TRUNCATE TABLE silver_passagem;")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 1;")

    cursor_raw = conexao.cursor(dictionary=True, buffered=True)
    # Garante integridade referencial: só importa passagens que possuem uma viagem válida na silver_viagem
    cursor_raw.execute("""
        SELECT rp.* FROM raw_passagem rp
        INNER JOIN silver_viagem sv ON rp.identificador_do_processo_de_viagem = sv.id_viagem;
    """)
    
    lote = []
    sql_insert = """
        INSERT INTO silver_passagem (
            id_viagem, meio_transporte, pais_origem_ida, uf_origem_ida, cidade_origem_ida,
            pais_destino_ida, uf_destino_ida, cidade_destino_ida, valor_passagem,
            taxa_servico, data_emissao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    for linha in cursor_raw:
        valor_passagem = tratar_decimal(linha.get("valor_da_passagem"))
        taxa_servico = tratar_decimal(linha.get("taxa_de_servico"))
        emissao = tratar_data(linha.get("data_da_emissao_compra"))
        
        registro = (
            linha.get("identificador_do_processo_de_viagem"),
            linha.get("meio_transporte"),
            linha.get("pais_origem_ida"),
            linha.get("uf_origem_ida"),
            linha.get("cidade_origem_ida"),
            linha.get("pais_destino_ida"),
            linha.get("uf_destino_ida"),
            linha.get("cidade_destino_ida"),
            valor_passagem,
            taxa_servico,
            emissao
        )
        lote.append(registro)
        
        if len(lote) >= TAMANHO_BLOCO:
            inserir_em_lote(conexao, sql_insert, lote)
            lote = []
            
    if lote:
        inserir_em_lote(conexao, sql_insert, lote)
        
    cursor_raw.close()
    print(" Carga de silver_passagem finalizada com sucesso!")


def transformar_pagamentos(conexao):
    print(" Transformando dados para silver_pagamento...")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 0;")
    executar(conexao, "TRUNCATE TABLE silver_pagamento;")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 1;")

    cursor_raw = conexao.cursor(dictionary=True, buffered=True)
    # Garante integridade referencial
    cursor_raw.execute("""
        SELECT rpag.* FROM raw_pagamento rpag
        INNER JOIN silver_viagem sv ON rpag.identificador_do_processo_de_viagem = sv.id_viagem;
    """)
    
    lote = []
    sql_insert = """
        INSERT INTO silver_pagamento (
            id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora, tipo_pagamento, valor
        ) VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    for linha in cursor_raw:
        valor = tratar_decimal(linha.get("valor"))
        tipo_pag = linha.get("tipo_de_pagamento") or "NÃO INFORMADO"
        
        registro = (
            linha.get("identificador_do_processo_de_viagem"),
            linha.get("numero_da_proposta_pcdp"),
            linha.get("nome_do_orgao_pagador"),
            linha.get("nome_da_unidade_gestora_pagadora"),
            tipo_pag,
            valor
        )
        lote.append(registro)
        
        if len(lote) >= TAMANHO_BLOCO:
            inserir_em_lote(conexao, sql_insert, lote)
            lote = []
            
    if lote:
        inserir_em_lote(conexao, sql_insert, lote)
        
    cursor_raw.close()
    print(" Carga de silver_pagamento finalizada com sucesso!")


def transformar_trechos(conexao):
    print(" Transformando dados para silver_trecho...")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 0;")
    executar(conexao, "TRUNCATE TABLE silver_trecho;")
    executar(conexao, "SET FOREIGN_KEY_CHECKS = 1;")

    cursor_raw = conexao.cursor(dictionary=True, buffered=True)
    # Garante integridade referencial
    cursor_raw.execute("""
        SELECT rt.* FROM raw_trecho rt
        INNER JOIN silver_viagem sv ON rt.identificador_do_processo_de_viagem = sv.id_viagem;
    """)
    
    lote = []
    sql_insert = """
        INSERT INTO silver_trecho (
            id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
            destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    for linha in cursor_raw:
        diarias = tratar_decimal(linha.get("numero_diarias"))
        origem_data = tratar_data(linha.get("origem_data"))
        destino_data = tratar_data(linha.get("destino_data"))
        seq = linha.get("sequencia_trecho")
        
        try:
            seq = int(seq) if seq else None
        except ValueError:
            seq = None
            
        registro = (
            linha.get("identificador_do_processo_de_viagem"),
            seq,
            origem_data,
            linha.get("origem_uf"),
            linha.get("origem_cidade"),
            destino_data,
            linha.get("destino_uf"),
            linha.get("destino_cidade"),
            linha.get("meio_transporte"),
            diarias
        )
        lote.append(registro)
        
        if len(lote) >= TAMANHO_BLOCO:
            inserir_em_lote(conexao, sql_insert, lote)
            lote = []
            
    if lote:
        inserir_em_lote(conexao, sql_insert, lote)
        
    cursor_raw.close()
    print(" Carga de silver_trecho finalizada com sucesso!")


def main():
    try:
        print("\n Conectando ao MySQL para a fase de Transformação...")
        conexao = conectar()
        
        # Ordem de execução estrita para não violar chaves estrangeiras (FK)
        transformar_viagens(conexao)
        transformar_passagens(conexao)
        transformar_pagamentos(conexao)
        transformar_trechos(conexao)
        
        conexao.close()
        print("\n Fase 2 (Transformação - Camada Silver) concluída com 100% de sucesso!")
        
    except Exception as e:
        print(f"\n Ocorreu um erro crítico durante a fase de transformação: {e}")


if __name__ == "__main__":
    main()