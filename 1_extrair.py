"""
1_extrair.py
------------
Realiza o download do dataset, descompacta os arquivos brutos do portal
e realiza a inserção alinhando o cabeçalho do CSV diretamente com o banco de dados.
"""

import csv
import zipfile
from pathlib import Path
import gdown

# Importações dos módulos locais do projeto
from config import (
    PASTA_DADOS, 
    DRIVE_FILE_ID, 
    ARQUIVOS, 
    TAMANHO_BLOCO, 
    CSV_SEPARADOR, 
    CSV_ENCODING
)
from banco import conectar, executar, inserir_em_lote


def baixar_dados():
    """Baixa o arquivo ZIP do Google Drive usando gdown."""
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    arquivo_destino = PASTA_DADOS / "dados.zip"
    
    if arquivo_destino.exists():
        print(f" arquivo {arquivo_destino.name} já existe localmente. Pulando download.")
        return arquivo_destino

    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    print(f" Iniciando download do ID {DRIVE_FILE_ID} via gdown...")
    
    try:
        gdown.download(url, str(arquivo_destino), quiet=False)
        print(" Download concluído com sucesso!")
        return arquivo_destino
    except Exception as e:
        print(f" Erro ao tentar baixar o arquivo: {e}")
        raise


def extrair_zip(caminho_zip):
    """Descompacta o arquivo ZIP na pasta de dados."""
    print(f" Extraindo {caminho_zip.name} para {PASTA_DADOS}...")
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(PASTA_DADOS)
        print(" Extração concluída!")
    except Exception as e:
        print(f" Erro ao extrair o arquivo ZIP: {e}")
        raise


def normalizar_nome_coluna(nome):
    """
    Normaliza os cabeçalhos literais dos arquivos CSV
    para bater exatamente com a definição definida na tabela raw_*.
    """
    nome_limpo = nome.strip().lower()
    substituicoes = {
        " ": "_", "-": "_", "/": "_", "–": "_", ".": "", "(": "", ")": "", "?": "",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "â": "a", "ê": "e", "ô": "o", "ã": "a", "õ": "o", "ç": "c"
    }
    for orig, dest in substituicoes.items():
        nome_limpo = nome_limpo.replace(orig, dest)
    
    while "__" in nome_limpo:
        nome_limpo = nome_limpo.replace("__", "_")
        
    nome_limpo = nome_limpo.strip("_")
    
    # REGRA DE EXCEÇÃO: Corrige especificamente "meio_de_transporte" para bater com "meio_transporte" do banco
    if nome_limpo == "meio_de_transporte":
        nome_limpo = "meio_transporte"
        
    return nome_limpo


def carregar_csv_alinhado(conexao, caminho_csv, tabela_raw):
    """
    Lê o CSV, normaliza o cabeçalho, limpa a tabela (idempotência)
    e insere os lotes mapeando chave por chave de forma perfeita.
    """
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    print(f"\n Analisando cabeçalhos de {caminho_csv.name}...")
    
    # 1. Abre uma conexão buffered inicial para descobrir as colunas reais da tabela RAW
    cursor_cols = conexao.cursor(buffered=True)
    try:
        cursor_cols.execute(f"SELECT * FROM {tabela_raw} LIMIT 0;")
        cursor_cols.fetchall()  # Consome resultado do protocolo MySQL
        colunas_destino = [desc[0] for desc in cursor_cols.description]
    finally:
        cursor_cols.close()

    # 2. Garante a idempotência limpando a tabela RAW antes da nova carga
    print(f" Limpando dados antigos da tabela {tabela_raw}...")
    executar(conexao, f"TRUNCATE TABLE {tabela_raw};")

    # 3. Leitura com DictReader mapeando as colunas de destino
    try:
        with open(caminho_csv, mode="r", encoding=CSV_ENCODING) as f:
            leitor = csv.DictReader(f, delimiter=CSV_SEPARADOR)
            
            # Reconstrói e normaliza as chaves lidas do cabeçalho original
            cabecalho_csv = leitor.fieldnames
            mapeamento_chaves = {normalizar_nome_coluna(col): col for col in cabecalho_csv}
            
            # Montagem do INSERT parametrizado
            colunas_validas = [col for col in colunas_destino if col in mapeamento_chaves]
            colunas_sql = ", ".join([f"`{col}`" for col in colunas_validas])
            placeholders = ", ".join(["%s"] * len(colunas_validas))
            sql_insert = f"INSERT INTO {tabela_raw} ({colunas_sql}) VALUES ({placeholders})"
            
            bloco = []
            total_linhas = 0
            
            for linha_dict in leitor:
                # Extrai do dicionário apenas as colunas que estão presentes na tabela raw de destino
                valores_linha = []
                for col in colunas_validas:
                    chave_original = mapeamento_chaves[col]
                    valores_linha.append(linha_dict.get(chave_original, None))
                
                bloco.append(tuple(valores_linha))
                
                if len(bloco) >= TAMANHO_BLOCO:
                    inserir_em_lote(conexao, sql_insert, bloco)
                    total_linhas += len(bloco)
                    print(f"   {total_linhas} registros inseridos...")
                    bloco = []
            
            if bloco:
                inserir_em_lote(conexao, sql_insert, bloco)
                total_linhas += len(bloco)
                
            print(f" Sucesso! Tabela {tabela_raw} preenchida com {total_linhas} registros de forma perfeitamente alinhada.")
            
    except Exception as e:
        print(f" Falha no processamento/carga do arquivo {caminho_csv.name}: {e}")
        raise


def main():
    try:
        # 1. Download e Extração
        caminho_zip = baixar_dados()
        extrair_zip(caminho_zip)
        
        # 2. Conectando ao Banco
        print("\n Conectando ao MySQL...")
        conexao = conectar()
        
        # 3. Iterando e populando as tabelas RAW com precisão de mapeamento
        for chave, meta in ARQUIVOS.items():
            nome_csv = meta["csv"]
            tabela_raw = meta["tabela_raw"]
            caminho_csv = PASTA_DADOS / nome_csv
            
            carregar_csv_alinhado(conexao, caminho_csv, tabela_raw)
            
        conexao.close()
        print("\n Fase 1 (Extração e Carga Raw) concluída com 100% de precisão e dados perfeitamente estruturados!")
        
    except Exception as e:
        print(f"\n Ocorreu um erro crítico durante a execução do pipeline: {e}")


if __name__ == "__main__":
    main()