import os
import shutil
import logging


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
