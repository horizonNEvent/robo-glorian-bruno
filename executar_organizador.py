#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

# Adiciona o diretório ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent))

from organizador_arquivos import organizar_arquivos

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    pasta = r"D:\Downloads\glorian"

    if not Path(pasta).exists():
        print(f"❌ Erro: A pasta '{pasta}' não existe!")
        sys.exit(1)

    print(f"Organizando arquivos em: {pasta}")
    print("-" * 60)

    organizar_arquivos(pasta, logger)

    print("-" * 60)
    print("Organização concluída!")
