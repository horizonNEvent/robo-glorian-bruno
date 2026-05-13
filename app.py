import streamlit as st
import logging
import sys
from pathlib import Path

# Adiciona o diretório ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent))
from organizador_arquivos import organizar_arquivos_upload

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
    st.write("Esta ferramenta organiza arquivos XML e PDF, agrupando-os por Chave da Nota Fiscal em pastas correspondentes.")

    # Upload de arquivos
    st.subheader("📤 Faça Upload dos Arquivos")
    uploaded_files = st.file_uploader(
        "Selecione os arquivos XML e PDF",
        type=["xml", "pdf"],
        accept_multiple_files=True,
        help="Você pode selecionar vários arquivos de uma vez"
    )

    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")

    if st.button("Organizar Arquivos", type="primary", disabled=not uploaded_files):
        if not uploaded_files:
            st.warning("Por favor, faça upload de pelo menos um arquivo.")
            return

        st.success("Iniciando organização...")

        # Container para os logs
        st.subheader("📋 Logs da Execução")
        log_placeholder = st.empty()

        # Configura o logger
        logger = logging.getLogger("streamlit_logger")
        logger.setLevel(logging.INFO)

        # Limpa os handlers antigos
        if logger.hasHandlers():
            logger.handlers.clear()

        sl_handler = StreamlitHandler(log_placeholder)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        sl_handler.setFormatter(formatter)
        logger.addHandler(sl_handler)

        with st.spinner("Organizando os arquivos..."):
            try:
                # Processa os arquivos e gera ZIP
                zip_content = organizar_arquivos_upload(uploaded_files, logger)

                st.balloons()
                st.success("✅ Organização concluída com sucesso!")

                # Botão para download
                st.subheader("📥 Download")
                st.download_button(
                    label="⬇️ Baixar Arquivos Organizados (ZIP)",
                    data=zip_content,
                    file_name="arquivos_organizados.zip",
                    mime="application/zip",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ Ocorreu um erro durante a organização: {e}")

if __name__ == "__main__":
    main()
