import os
import shutil
import logging
from collections import defaultdict
import zipfile
import io


def organizar_arquivos(pasta_origem, logger=None):
    """
    Organiza os arquivos baixados agrupando por Chave/Número da NF.
    Baseado no padrão:
      - NFe[CHAVE]... (XML e PDF)
      - boleto-NFe[CHAVE]... (PDF)

    Args:
        pasta_origem: Caminho da pasta com os arquivos a organizar
        logger: Logger para registrar operações (opcional)
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info("Iniciando organização dos arquivos...")
    arquivos_por_nf = {}

    try:
        for arquivo in os.listdir(pasta_origem):
            path_completo = os.path.join(pasta_origem, arquivo)
            if os.path.isdir(path_completo):
                continue

            nf_chave = None

            # Extração da chave
            # Ex: NFe1226014307611700024... -> 1226014307611700024...
            # Ex: boleto-NFe1226014307611700024...

            if arquivo.startswith('NFe'):
                # Padrão: NFe[44 digitos]...
                # Tenta extrair os primeiros 44 caracteres após NFe
                try:
                    potential_key = arquivo[3:47]  # NFe + 44 chars
                    if potential_key.isdigit() and len(potential_key) == 44:
                        nf_chave = potential_key
                except:
                    pass

            elif arquivo.startswith('boleto-NFe'):
                # Padrão: boleto-NFe[44 digitos]...
                try:
                    potential_key = arquivo[10:54]  # boleto-NFe + 44 chars
                    if potential_key.isdigit() and len(potential_key) == 44:
                        nf_chave = potential_key
                except:
                    pass

            if nf_chave:
                if nf_chave not in arquivos_por_nf:
                    arquivos_por_nf[nf_chave] = []
                arquivos_por_nf[nf_chave].append(arquivo)

        # Move arquivos
        for chave, lista_arquivos in arquivos_por_nf.items():
            if not lista_arquivos:
                continue

            nome_pasta = f"NF_{chave}"
            nova_pasta = os.path.join(pasta_origem, nome_pasta)
            os.makedirs(nova_pasta, exist_ok=True)

            for arq in lista_arquivos:
                src = os.path.join(pasta_origem, arq)
                dst = os.path.join(nova_pasta, arq)
                try:
                    shutil.move(src, dst)
                    logger.info(f"Movido: {arq} -> {nome_pasta}")
                except Exception as e:
                    logger.error(f"Erro ao mover {arq}: {e}")

        logger.info("Organização concluída.")

    except Exception as e:
        logger.error(f"Erro na organização: {e}")


def extrair_e_organizar_zip(zip_file, logger=None):
    """
    Extrai um ZIP e organiza os arquivos dentro dele.

    Args:
        zip_file: Arquivo ZIP feito upload do Streamlit
        logger: Logger para registrar operações (opcional)

    Returns:
        bytes: Conteúdo do novo ZIP com os arquivos organizados
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info("Extraindo arquivos do ZIP...")

    # Lê o ZIP feito upload
    try:
        with zipfile.ZipFile(zip_file) as zip_entrada:
            arquivos_lista = []

            # Extrai todos os arquivos e prepara para processamento
            for nome_arquivo in zip_entrada.namelist():
                # Pula diretórios
                if nome_arquivo.endswith('/'):
                    continue

                # Pega apenas o nome do arquivo (remove diretórios do ZIP original)
                nome_simples = nome_arquivo.split('/')[-1]

                # Filtra apenas XML e PDF
                if nome_simples.lower().endswith(('.xml', '.pdf')):
                    conteudo = zip_entrada.read(nome_arquivo)
                    arquivos_lista.append((nome_simples, conteudo))
                    logger.info(f"Extraído: {nome_arquivo}")

            if not arquivos_lista:
                raise ValueError("Nenhum arquivo XML ou PDF encontrado no ZIP!")

            logger.info(f"Total de arquivos extraídos: {len(arquivos_lista)}")
    except zipfile.BadZipFile:
        raise ValueError("Arquivo não é um ZIP válido!")

    # Agrupa por chave de NF
    arquivos_por_nf = defaultdict(list)

    for nome_arquivo, conteudo in arquivos_lista:
        nf_chave = None

        # Extração da chave (mesmo padrão anterior)
        if nome_arquivo.startswith('NFe'):
            try:
                potential_key = nome_arquivo[3:47]  # NFe + 44 chars
                if potential_key.isdigit() and len(potential_key) == 44:
                    nf_chave = potential_key
            except:
                pass

        elif nome_arquivo.startswith('boleto-NFe'):
            try:
                potential_key = nome_arquivo[10:54]  # boleto-NFe + 44 chars
                if potential_key.isdigit() and len(potential_key) == 44:
                    nf_chave = potential_key
            except:
                pass

        if nf_chave:
            arquivos_por_nf[nf_chave].append((nome_arquivo, conteudo))
            logger.info(f"Agrupado: {nome_arquivo} -> NF_{nf_chave}")
        else:
            logger.warning(f"⚠️ Não foi possível extrair chave de NF de: {nome_arquivo}")

    # Cria ZIP com estrutura organizada
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for chave, arquivos in arquivos_por_nf.items():
            pasta_nf = f"NF_{chave}"
            for nome_arquivo, conteudo in arquivos:
                caminho_zip = f"{pasta_nf}/{nome_arquivo}"
                zip_file.writestr(caminho_zip, conteudo)
                logger.info(f"Adicionado ao ZIP: {caminho_zip}")

    zip_buffer.seek(0)
    logger.info("✅ ZIP criado com sucesso!")
    return zip_buffer.getvalue()


def organizar_arquivos_upload(arquivos_upload, logger=None):
    """
    Organiza arquivos feitos upload, retornando um ZIP com a estrutura organizada.

    Args:
        arquivos_upload: Lista de uploaded files do Streamlit
        logger: Logger para registrar operações (opcional)

    Returns:
        bytes: Conteúdo do ZIP com os arquivos organizados
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info(f"Processando {len(arquivos_upload)} arquivo(s)...")
    arquivos_por_nf = defaultdict(list)

    # Agrupa arquivos por chave de NF
    for uploaded_file in arquivos_upload:
        arquivo = uploaded_file.name
        nf_chave = None

        # Extração da chave (mesmo padrão anterior)
        if arquivo.startswith('NFe'):
            try:
                potential_key = arquivo[3:47]  # NFe + 44 chars
                if potential_key.isdigit() and len(potential_key) == 44:
                    nf_chave = potential_key
            except:
                pass

        elif arquivo.startswith('boleto-NFe'):
            try:
                potential_key = arquivo[10:54]  # boleto-NFe + 44 chars
                if potential_key.isdigit() and len(potential_key) == 44:
                    nf_chave = potential_key
            except:
                pass

        if nf_chave:
            arquivos_por_nf[nf_chave].append((arquivo, uploaded_file.getbuffer()))
            logger.info(f"Agrupado: {arquivo} -> NF_{nf_chave}")
        else:
            logger.warning(f"⚠️ Não foi possível extrair chave de NF de: {arquivo}")

    # Cria ZIP com estrutura organizada
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for chave, arquivos in arquivos_por_nf.items():
            pasta_nf = f"NF_{chave}"
            for nome_arquivo, conteudo in arquivos:
                caminho_zip = f"{pasta_nf}/{nome_arquivo}"
                zip_file.writestr(caminho_zip, conteudo)
                logger.info(f"Adicionado ao ZIP: {caminho_zip}")

    zip_buffer.seek(0)
    logger.info("✅ ZIP criado com sucesso!")
    return zip_buffer.getvalue()
