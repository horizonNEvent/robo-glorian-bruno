import streamlit as st
import logging
import sys
from pathlib import Path

# Adiciona o diretório ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent))
from organizador_arquivos import organizar_arquivos

class StreamlitHandler(logging.Handler):
    """Handler customizado para exibir os logs na tela do Streamlit"""
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.log_text = ""

    def emit(self, record):
        msg = self.format(record)
        self.log_text += f"{msg}\n"
        self.placeholder.text(self.log_text)

def main():
    st.set_page_config(page_title="Organizador de NFs", page_icon="📁", layout="centered")
    
    st.title("📁 Organizador de Notas Fiscais e Boletos")
    st.write("Esta ferramenta organiza arquivos XML e PDF baixados, agrupando-os por Chave da Nota Fiscal em pastas correspondentes.")

    # Input do caminho da pasta
    pasta_origem = st.text_input("Caminho da pasta com os arquivos:", value=r"D:\Downloads\glorian")

    if st.button("Organizar Arquivos", type="primary"):
        if not pasta_origem:
            st.warning("Por favor, informe o caminho da pasta.")
            return
            
        path = Path(pasta_origem)
        if not path.exists():
            st.error(f"❌ Erro: A pasta '{pasta_origem}' não existe!")
            return
            
        if not path.is_dir():
            st.error(f"❌ Erro: O caminho '{pasta_origem}' não é uma pasta válida!")
            return

        st.success("Iniciando organização...")
        
        # Container para os logs
        st.subheader("Logs da Execução")
        
        # Usamos uma caixa de texto scrollável para os logs (st.code ou st.text dentro de um container)
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
        
        # Configura o logger para jogar a saída no Streamlit
        logger = logging.getLogger("streamlit_logger")
        logger.setLevel(logging.INFO)
        
        # Limpa os handlers antigos caso o botão seja clicado várias vezes
        if logger.hasHandlers():
            logger.handlers.clear()
            
        sl_handler = StreamlitHandler(log_placeholder)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        sl_handler.setFormatter(formatter)
        logger.addHandler(sl_handler)

        with st.spinner("Organizando os arquivos..."):
            try:
                organizar_arquivos(str(path), logger)
                st.balloons()
                st.success("✅ Organização concluída com sucesso!")
            except Exception as e:
                st.error(f"Ocorreu um erro durante a organização: {e}")

if __name__ == "__main__":
    main()
